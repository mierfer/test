"""AEN Blog — 启动入口

    python run.py             # 仅本机访问 (127.0.0.1:5000)
    python run.py --lan       # 局域网访问   (0.0.0.0:5000)
    python run.py --public    # 公网访问     (ngrok 隧道)

    gunicorn run:app          # 生产部署 (Render 等平台)
"""
import os
import secrets
import sys
from app import create_app

app = create_app()


def _start_ngrok(port: int) -> str | None:
    """Start an ngrok HTTP tunnel via pyngrok API. Returns the public URL or None."""
    try:
        from pyngrok import ngrok

        tunnel = ngrok.connect(port, "http", bind_tls=True)
        url = str(tunnel.public_url)
        return url
    except ImportError:
        print("  ⚠️  未安装 pyngrok, 请执行: pip install pyngrok")
    except Exception as exc:
        print(f"  ⚠️  ngrok 隧道启动失败: {exc}")
    return None


if __name__ == "__main__":
    # Render provides PORT env; default to 5000 for local dev
    port = int(os.environ.get("PORT", 5000))
    host = "127.0.0.1"
    public_mode = "--public" in sys.argv
    lan_mode = "--lan" in sys.argv or public_mode
    remote_mode = lan_mode or public_mode or bool(os.environ.get("RENDER"))

    if lan_mode or os.environ.get("RENDER"):
        host = "0.0.0.0"

    # ---- Network security checks ----
    if remote_mode:
        debug = False
        print("  🔒 安全: 已禁用 DEBUG 模式 (非本机访问)")
    else:
        debug = True

    if remote_mode and app.config["SECRET_KEY"] == "aen-blog-secret-key-change-in-production":
        new_key = secrets.token_hex(32)
        print("  ⚠️  安全警告: 正在使用默认 SECRET_KEY, 请设置环境变量:")
        print(f"     export SECRET_KEY={new_key}")
        app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", new_key)
        print("  ℹ️  本次已使用临时随机密钥")

    public_url = None

    if public_mode:
        print("\n  🔗 正在启动 ngrok 隧道...")
        public_url = _start_ngrok(port)
        if public_url:
            print(f"  ✅ 公网链接: {public_url}")
        else:
            print("  ℹ️  回退到局域网模式，手动端口转发后也可公网访问")

    print(f"\n  AEN Blog 运行中 → http://{host}:{port}\n")

    try:
        app.run(host=host, port=port, debug=debug)
    finally:
        if public_url:
            try:
                from pyngrok import ngrok

                ngrok.disconnect(public_url)
            except Exception:
                pass
