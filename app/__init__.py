from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config["default"]))

    db.init_app(app)
    login_manager.init_app(app)

    @app.context_processor
    def inject_nav_categories():
        from app.models import Category
        return {"get_nav_categories": lambda: Category.query.limit(6).all()}

    from app.security import init_security
    init_security(app)

    from app.auth import auth as auth_bp
    from app.blog import blog as blog_bp
    from app.admin import admin as admin_bp
    from app.api import api as api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        from app.models import User, Post, Category, Tag, Comment  # noqa

        db.create_all()
        _seed_defaults()

    return app


def _seed_defaults():
    from app.models import User, Category, Post

    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", email="admin@aen.local", is_admin=True)
        admin.set_password("admin123")
        db.session.add(admin)

    default_categories = [
        {"name": "AE基础教程", "slug": "ae-basics", "description": "After Effects 入门与基础操作教程"},
        {"name": "特效制作", "slug": "vfx", "description": "视觉特效与合成技术"},
        {"name": "MG动画", "slug": "motion-graphics", "description": "动态图形设计与Motion Graphics"},
        {"name": "插件推荐", "slug": "plugins", "description": "AE实用插件评测与推荐"},
        {"name": "模板分享", "slug": "templates", "description": "AE模板资源分享与使用技巧"},
        {"name": "行业资讯", "slug": "industry-news", "description": "影视后期行业动态与资讯"},
    ]
    for cat in default_categories:
        if not Category.query.filter_by(slug=cat["slug"]).first():
            db.session.add(Category(**cat))

    db.session.commit()

    # Seed demo posts if none exist
    if Post.query.count() == 0:
        from app.models import Tag

        admin_user = User.query.filter_by(username="admin").first()
        cats = {c.slug: c for c in Category.query.all()}

        posts_data = [
            {
                "title": "After Effects 2026 新功能完全解析",
                "slug": "ae-2026-new-features",
                "summary": "Adobe After Effects 2026 版本带来了多项重大更新，包括AI驱动的Roto Brush 3.0、实时3D渲染引擎改进等。",
                "content": """<h2>After Effects 2026 重大更新</h2>
<p>Adobe 在 After Effects 2026 中引入了多项令人兴奋的新功能，极大地提升了动态图形和视觉特效的工作效率。</p>

<h3>1. AI 驱动的 Roto Brush 3.0</h3>
<p>全新的 Roto Brush 3.0 利用 Adobe Sensei AI 技术，提供前所未有的抠像精度。即使处理复杂的毛发边缘和透明物体，也能实现精确的Alpha遮罩。处理速度相比上一代提升了约40%。</p>

<h3>2. 实时3D渲染引擎</h3>
<p>AE 2026 对内置的 Cinema 4D 渲染引擎进行了重大优化。现在可以直接在视口中进行实时的3D场景预览，无需等待漫长的渲染。这对于处理复杂的3D文字动画和场景组合非常有帮助。</p>

<h3>3. 增强的属性面板</h3>
<p>全新的属性面板支持关键词搜索，可以快速定位到需要的属性。同时支持自定义属性收藏夹，将常用的效果和属性集中管理。</p>

<blockquote>AE 2026 是一次值得升级的版本更新，AI功能的加入让很多繁琐的操作变得简单高效。</blockquote>

<h3>4. 多帧渲染改进</h3>
<p>多帧渲染（Multi-Frame Rendering）现在支持更多的第三方插件，渲染速度进一步提升。对于使用复杂特效链的项目，渲染时间可以减少30-50%。</p>

<p>总的来说，AE 2026 是一次非常扎实的更新，推荐所有AE用户升级体验。</p>""",
                "category_slug": "industry-news",
                "tags": ["AE2026", "新功能", "Adobe"],
                "is_featured": True,
            },
            {
                "title": "AE表达式入门：从零开始掌握动画自动化",
                "slug": "ae-expressions-beginner",
                "summary": "学习AE表达式的基础语法和常用技巧，让你的动画制作效率翻倍。适合零基础的新手入门。",
                "content": """<h2>什么是AE表达式？</h2>
<p>表达式是After Effects中基于JavaScript的小型脚本，可以自动控制图层属性，创建复杂的动画效果，而不需要手动设置关键帧。</p>

<h3>基础语法</h3>
<p>表达式从最基本的开始——<code>wiggle()</code> 函数。这是最常用的表达式之一：</p>

<pre><code>wiggle(5, 30)</code></pre>

<p>这行代码会使图层每秒随机抖动5次，幅度为30像素。简单一行代码，就替代了可能需要几十个关键帧才能完成的工作。</p>

<h3>常用表达式技巧</h3>

<h4>1. 循环动画 — loopOut()</h4>
<p>当你制作了一个关键帧动画，想要它无限循环：</p>
<pre><code>loopOut("cycle")</code></pre>

<h4>2. 时间控制 — time</h4>
<p>使用 <code>time</code> 变量可以创建基于时间的动画：</p>
<pre><code>time * 100</code></pre>
<p>这会让属性值每秒增加100，非常适合制作持续的旋转或位置移动。</p>

<h4>3. 惯性衰减</h4>
<p>模拟物理惯性效果，让动画更有质感：</p>
<pre><code>amp = 0.8;
freq = 2;
decay = 4;

n = 0;
if (numKeys > 0){
  n = nearestKey(time).index;
  if (key(n).time > time) n--;
}
if (n > 0){
  t = time - key(n).time;
  v = velocityAtTime(key(n).time - thisComp.frameDuration/10);
  value + v * amp * Math.sin(freq * t * 2 * Math.PI) / Math.exp(decay * t);
} else {
  value;
}</code></pre>

<blockquote>掌握表达式是提升AE技能的关键一步。它让你从"手工艺人"升级为"自动化工程师"。</blockquote>

<h3>学习路径建议</h3>
<ul>
  <li>先理解wiggle、time、loopOut三个基础函数</li>
  <li>学习使用变量和简单的数学运算</li>
  <li>掌握条件语句（if/else）和线性插值（linear/ease）</li>
  <li>尝试将多个表达式组合使用</li>
</ul>""",
                "category_slug": "ae-basics",
                "tags": ["表达式", "入门", "自动化", "wiggle"],
                "is_featured": True,
            },
            {
                "title": "打造赛博朋克风格标题 — AE发光文字特效教程",
                "slug": "cyberpunk-title-effect",
                "summary": "手把手教你使用After Effects制作赛博朋克风格的霓虹发光标题，包含调色和特效合成的完整流程。",
                "content": """<h2>赛博朋克风格：霓虹发光文字</h2>
<p>赛博朋克（Cyberpunk）是近年来非常流行的视觉风格。本教程将演示如何使用AE制作充满未来感的霓虹发光标题动画。</p>

<h3>步骤一：创建文字图层</h3>
<p>使用文字工具创建你的标题。推荐使用粗体的无衬线字体，如 Impact、Arial Black 或下载专门的赛博朋克字体。</p>

<h3>步骤二：添加发光效果</h3>
<p>这是核心步骤。给文字图层添加以下效果：</p>
<ol>
  <li><strong>Glow（发光）</strong> — 设置 Glow Radius 为 40-60，Glow Intensity 为 2-3</li>
  <li><strong>CC Light Sweep</strong> — 添加光线扫描效果，模拟霓虹灯管的流动感</li>
  <li><strong>Drop Shadow</strong> — 为文字添加彩色投影，颜色选择品红或青色</li>
</ol>

<h3>步骤三：背景处理</h3>
<p>赛博朋克风格的背景通常包含以下元素：</p>
<ul>
  <li>深色底色（深蓝、暗紫或纯黑）</li>
  <li>网格线条（使用 Grid 效果或 Fractal Noise）</li>
  <li>粒子效果（使用 Particular 或 CC Particle World）</li>
</ul>

<pre><code>// 使用 Fractal Noise 创建动态背景
// 添加以下表达式到 Evolution 属性：
time * 60</code></pre>

<h3>步骤四：颜色分级</h3>
<p>使用 Lumetri Color 或 Color Balance 进行最终调色。赛博朋克风格的经典配色方案：</p>
<ul>
  <li>主色：品红 (#FF006E) + 青色 (#00F0FF)</li>
  <li>辅助色：深紫 (#2D0060) + 暗蓝 (#0A0020)</li>
  <li>点缀色：霓虹黄 (#FFFF00) 用于强调</li>
</ul>

<blockquote>好的赛博朋克风格作品，关键在于光与暗的对比——让发光的部分足够亮，让暗部真正暗下去。</blockquote>

<h3>步骤五：动画微调</h3>
<p>使用关键帧添加文字的入场动画。推荐的组合：缩放（从120%到100%）+ 透明度（从0到100%）+ 轻微的Y轴位移。为关键帧添加缓入缓出效果，让动画更加流畅。</p>""",
                "category_slug": "vfx",
                "tags": ["赛博朋克", "发光", "文字特效", "调色"],
                "is_featured": True,
            },
            {
                "title": "MG动画神器：Duik 全面使用指南",
                "slug": "duik-complete-guide",
                "summary": "Duik是AE最强大的角色动画插件之一。本指南详细介绍Duik的骨骼绑定、自动动画和控制器功能。",
                "content": """<h2>Duik — MG动画师的必备工具</h2>
<p>Duik（Duduf IK Tools）是一款免费开源的After Effects角色动画插件，提供了专业的骨骼绑定和动画工具。它是制作MG角色动画的首选方案。</p>

<h3>安装与设置</h3>
<p>Duik 可以通过以下方式安装：</p>
<ol>
  <li>访问 <code>rxlaboratory.org</code> 下载最新版本</li>
  <li>使用AE的Script UI Panel安装</li>
  <li>或通过Aescripts + Aeplugins平台一键安装</li>
</ol>

<h3>核心功能详解</h3>

<h4>1. IK/FK 骨骼系统</h4>
<p>Duik 的骨骼系统支持正向运动学（FK）和反向运动学（IK）。IK特别适合制作角色手臂和腿部的自然运动——只需要移动手部，整个手臂就会自动跟随。</p>

<p>创建骨骼链的步骤：</p>
<pre><code>选择图层 → Duik面板 → Bones → Create Bones</code></pre>

<h4>2. Auto-Rig（自动绑定）</h4>
<p>这是Duik最强大的功能之一。你只需要标记出角色的关节位置，Auto-Rig会自动创建完整的骨骼结构、控制器和动画参数。</p>

<h4>3. 动画控制器</h4>
<p>Duik 创建的可视化控制器让动画调整变得直观：</p>
<ul>
  <li>位移控制器 — 拖拽即可移动角色部位</li>
  <li>旋转控制器 — 精确控制关节旋转</li>
  <li>滑块控制器 — 用于表情和细节动画</li>
</ul>

<h3>工作流程建议</h3>
<ol>
  <li>在Illustrator中设计角色，分层导入AE</li>
  <li>使用Duik创建骨骼结构</li>
  <li>添加自动绑定生成控制器</li>
  <li>为控制器设置关键帧制作动画</li>
  <li>使用Duik的动画工具（如Wiggle、Spring）添加细节</li>
</ol>

<blockquote>Duik 的学习曲线略陡，但一旦掌握，它能让你的角色动画制作效率提升数倍。</blockquote>

<h3>进阶技巧</h3>
<p>Duik 还包含了弹簧动画、随机摆动、路径动画等工具。特别推荐 Spring 工具——它可以为任何属性创建自然的弹性缓动效果，比手动调整关键帧曲线要快得多。</p>""",
                "category_slug": "plugins",
                "tags": ["Duik", "MG动画", "角色动画", "插件", "骨骼绑定"],
                "is_featured": False,
            },
            {
                "title": "5个提升AE渲染速度的实用技巧",
                "slug": "speed-up-ae-rendering",
                "summary": "渲染慢是AE用户最大的痛点。本文分享5个经过验证的加速方法，帮你省下大量等待时间。",
                "content": """<h2>为什么AE渲染这么慢？</h2>
<p>After Effects的渲染速度一直是用户抱怨最多的问题。理解渲染原理后，我们可以通过一些技巧来显著提升速度。</p>

<h3>技巧一：优化合成设置</h3>
<p>不要在每个合成中使用过高的分辨率。制作动画时，可以使用半分辨率预览和渲染测试，只在最终输出时才使用完整分辨率。</p>

<h3>技巧二：管理图层和效果</h3>
<ul>
  <li>关闭不需要的图层可见性（眼睛图标）——AE在渲染时会跳过不可见图层</li>
  <li>在预览时降低图层质量（从"最佳"改为"草稿"）</li>
  <li>将已完成的部分预渲染为视频文件，替换复杂的合成</li>
</ul>

<h3>技巧三：使用代理文件</h3>
<p>对于高分辨率素材，创建低分辨率的代理文件进行编辑。最终渲染时再切换回原始素材。这是处理4K/8K素材时的标准做法。</p>

<h3>技巧四：合理使用多帧渲染</h3>
<p>AE 2022及以后版本支持多帧渲染（Multi-Frame Rendering）。确保在首选项中启用了此功能，并为AE分配足够的内存：</p>
<pre><code>编辑 → 首选项 → 内存和性能
→ RAM分配给Adobe After Effects: 建议80%以上</code></pre>

<h3>技巧五：清理缓存</h3>
<p>定期清理磁盘缓存和内存缓存可以预防AE变慢。设置缓存路径到SSD上也能提升性能：</p>
<pre><code>编辑 → 首选项 → 媒体和磁盘缓存
→ 选择SSD作为缓存文件夹</code></pre>

<blockquote>最好的渲染优化是养成良好的项目习惯——规范命名、合理分组、及时清理无用图层。</blockquote>""",
                "category_slug": "ae-basics",
                "tags": ["渲染", "性能优化", "技巧", "效率"],
                "is_featured": False,
            },
            {
                "title": "Particular粒子插件深度评测：制作震撼的粒子特效",
                "slug": "particular-review",
                "summary": "Trapcode Particular是AE最著名的粒子系统插件。这篇深度评测帮你了解它的全部核心功能。",
                "content": """<h2>Trapcode Particular — 粒子特效的终极方案</h2>
<p>Red Giant 的 Trapcode Particular 是After Effects最经典的第三方插件之一。从简单的雪花飘落到复杂的星系爆炸，Particular让粒子特效制作变得直观而强大。</p>

<h3>核心功能</h3>

<h4>1. 粒子发射器系统</h4>
<p>Particular 提供了多种发射器类型：</p>
<ul>
  <li><strong>Point（点发射）</strong> — 从单一焦点发射粒子</li>
  <li><strong>Box/Sphere（盒子/球体发射）</strong> — 3D空间中的体积发射</li>
  <li><strong>Layer（图层发射）</strong> — 从自定义图层形状发射</li>
  <li><strong>Light（灯光发射）</strong> — 从AE灯光发射粒子</li>
</ul>

<h4>2. 物理引擎</h4>
<p>Particular内置了完整的物理模拟系统，包括重力、风力、空气阻力、湍流等参数。这让粒子行为可以模拟真实的物理现象。</p>

<h4>3. 粒子样式</h4>
<p>支持多种粒子类型：</p>
<ul>
  <li>Sprite（精灵图）— 使用自定义图片作为粒子</li>
  <li>Star/Bubble（星形/气泡）— 内置形状</li>
  <li>Streaklet — 运动模糊粒子，模拟光线拖尾</li>
</ul>

<h3>实战案例：星空穿梭效果</h3>
<p>创建一个"穿梭星空"效果的关键参数设置：</p>
<ol>
  <li>发射器类型：Box，尺寸设置为你合成的3倍宽度</li>
  <li>粒子速度：Z轴负方向500-1000</li>
  <li>粒子生命：3-5秒</li>
  <li>粒子大小：2-4像素，随机变化20%</li>
  <li>添加Glow效果增加光感</li>
</ol>

<blockquote>Particular是每个AE设计师都应该掌握的插件。虽然价格不菲，但它的能力远超内置的CC Particle World。</blockquote>

<h3>价格与替代方案</h3>
<p>Particular 订阅费用约$30/月（Red Giant Complete套餐的一部分）。如果预算有限，可以先使用AE内置的 CC Particle World 和 CC Particle Systems II 作为替代，虽然功能不如Particular丰富，但也能完成基础的粒子特效。</p>""",
                "category_slug": "plugins",
                "tags": ["Particular", "粒子", "插件评测", "Red Giant"],
                "is_featured": False,
            },
            {
                "title": "免费AE模板资源推荐 — 2026最全合集",
                "slug": "free-ae-templates-2026",
                "summary": "整理了一批高质量的免费AE模板网站，涵盖片头、转场、字幕条、信息图等常用类型。",
                "content": """<h2>免费不等于低质量</h2>
<p>很多设计师以为免费AE模板就意味着质量差，其实不然。以下整理的这些网站，提供的免费模板质量完全可以用于商业项目。</p>

<h3>推荐网站</h3>

<h4>1. Mixkit (mixkit.co)</h4>
<p>提供大量高质量的免费视频素材和AE模板。所有模板都可以免费商用，无需署名。更新频率高，分类清晰。</p>

<h4>2. Motion Array</h4>
<p>虽然主要是付费订阅平台，但每月会提供一定数量的免费模板下载。质量极高，包括完整的项目文件和教程。</p>

<h4>3. Videezy</h4>
<p>专注于视频素材，也提供AE模板。免费用户每天有一定下载额度，素材涵盖各种风格。</p>

<h4>4. Videvo</h4>
<p>包含免费和付费两部分。免费模板需要通过筛选找到，但质量不错，特别是片头和转场类模板。</p>

<h3>使用模板的注意事项</h3>
<ul>
  <li>下载后先检查使用的字体是否已安装，缺少字体会导致模板无法正常渲染</li>
  <li>注意查看模板的AE版本要求，低版本可能无法打开高版本模板</li>
  <li>部分免费模板使用了付费插件（如Particular、Element 3D），使用前先检查依赖</li>
  <li>即使模板免费，也建议保留来源信息，必要时应署名</li>
</ul>

<blockquote>模板是起点而非终点。最好的使用方式是在模板基础上进行二次创作，让它真正成为你自己的作品。</blockquote>

<h3>如何快速适配模板</h3>
<p>拿到模板后，关注这几个方面快速定位需要修改的部分：</p>
<ol>
  <li>找到"Edit Here"或"Your Text"标记的合成和图层</li>
  <li>检查主控合成中的颜色控制层</li>
  <li>替换 Placeholder 占位素材</li>
  <li>调整时长和转场节奏匹配你的内容</li>
</ol>""",
                "category_slug": "templates",
                "tags": ["模板", "免费资源", "素材", "片头"],
                "is_featured": False,
            },
            {
                "title": "AE中3D场景搭建 — 从零到精通的完整指南",
                "slug": "ae-3d-scene-tutorial",
                "summary": "深入学习AE的3D空间，掌握摄像机、灯光、3D图层的综合运用，搭建令人惊叹的三维场景。",
                "content": """<h2>AE不只是2D工具</h2>
<p>许多初学者误以为After Effects只能做2D动画。实际上，AE拥有强大的3D工作空间，配合Camera和Light系统，可以创建令人惊艳的三维场景。</p>

<h3>基础知识</h3>

<h4>3D图层</h4>
<p>任何图层都可以通过勾选3D开关变为3D图层。3D图层多了Z轴（深度），可以进行X/Y/Z三个维度的旋转和位移。关键快捷键：</p>
<ul>
  <li><code>P</code> — 位置</li>
  <li><code>R</code> — 旋转（3D图层会显示方向和旋转两组属性）</li>
  <li><code>A</code> — 锚点</li>
  <li>按 <code>W</code> 旋转工具查看3D旋转控件</li>
</ul>

<h4>摄像机系统</h4>
<p>AE的摄像机模拟真实摄像机：</p>
<ul>
  <li><strong>焦距</strong> — 影响透视强度。广角（<35mm）产生夸张的透视，长焦（>85mm）压缩空间感</li>
  <li><strong>景深</strong> — 控制焦点范围，模糊非焦点区域</li>
  <li><strong>光圈</strong> — 影响景深和曝光</li>
</ul>

<h3>实战：搭建3D文字场景</h3>
<ol>
  <li>创建多个文字图层，全部开启3D</li>
  <li>在Z轴上分散文字：-200, -100, 0, 100, 200</li>
  <li>添加摄像机，设置关键帧实现穿梭动画</li>
  <li>添加环境光和聚光灯增强空间感</li>
  <li>使用Null Object作为摄像机父级，简化动画控制</li>
</ol>

<h3>进阶技巧</h3>
<p>结合表达式可以创建更复杂的3D动画：</p>
<pre><code>// 让图层始终朝向摄像机
lookAt(thisComp.activeCamera.position, position)</code></pre>

<blockquote>3D是AE学习的分水岭。掌握3D空间操作后，你的创作边界会扩展数倍，从平面设计真正进入动态视觉设计领域。</blockquote>""",
                "category_slug": "ae-basics",
                "tags": ["3D", "摄像机", "灯光", "空间"],
                "is_featured": True,
            },
        ]

        # Collect all unique tags first
        all_tag_names = set()
        for pd in posts_data:
            for t in pd.get("tags", []):
                all_tag_names.add(t)

        existing_tags = {t.name: t for t in Tag.query.filter(Tag.name.in_(all_tag_names)).all()}
        for tname in all_tag_names:
            if tname not in existing_tags:
                tag = Tag(name=tname, slug=Post.generate_slug(tname))
                db.session.add(tag)
                existing_tags[tname] = tag
        db.session.flush()

        for pd in posts_data:
            post = Post(
                title=pd["title"],
                slug=pd["slug"],
                summary=pd["summary"],
                content=pd["content"],
                author_id=admin_user.id,
                category_id=cats[pd["category_slug"]].id if pd["category_slug"] in cats else None,
                is_published=True,
                is_featured=pd.get("is_featured", False),
            )
            for tag_name in pd.get("tags", []):
                post.tags.append(existing_tags[tag_name])
            db.session.add(post)

        db.session.commit()
