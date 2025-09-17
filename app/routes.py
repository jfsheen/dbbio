from flask import Blueprint, render_template, request, jsonify, redirect, session, url_for, flash
from datetime import datetime, timedelta
from . import db
from .models import PlantResource, InsectResource
import os

main_bp = Blueprint('main', __name__)

# 系统首页
@main_bp.route('/')
def index():
    """系统首页"""
    # 获取统计信息
    plant_count = PlantResource.query.count()
    insect_count = InsectResource.query.count()
    total_count = plant_count + insect_count
    
    return render_template('index.html', 
                         plant_count=plant_count,
                         insect_count=insect_count,
                         total_count=total_count)


@main_bp.route('/api/stats')
def api_stats():
    """获取统计信息的API接口"""
    total_plants = PlantResource.query.count()
    families_count = db.session.query(PlantResource.family).distinct().count()
    countries_count = db.session.query(PlantResource.country).distinct().count()
    
    return jsonify({
        'total_plants': total_plants,
        'families_count': families_count,
        'countries_count': countries_count
    })

# 简单的管理员认证（实际应用中应该使用更安全的认证方式）
@main_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """管理员登录"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 简单的硬编码认证（实际应用中应该使用数据库和密码哈希）
        if username == 'admin' and password == 'admin123':  # 请在实际应用中更改默认密码
            session['is_admin'] = True
            flash('管理员登录成功', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('用户名或密码错误', 'danger')
    
    return render_template('admin/login.html')

@main_bp.route('/admin/logout')
def admin_logout():
    """管理员登出"""
    session.pop('is_admin', None)
    flash('已退出管理员模式', 'info')
    return redirect(url_for('main.index'))

@main_bp.errorhandler(404)
def not_found_error(error):
    """处理404错误"""
    return render_template('errors/404.html'), 404

@main_bp.errorhandler(500)
def internal_error(error):
    """处理500错误"""
    db.session.rollback()
    # 在开发环境中传递错误信息给模板
    if app.config['ENV'] == 'development':
        return render_template('errors/500.html', error=error, now=datetime.now()), 500
    else:
        return render_template('errors/500.html'), 500

@main_bp.errorhandler(403)
def forbidden_error(error):
    """处理403错误"""
    return render_template('errors/403.html'), 403

@main_bp.errorhandler(400)
def bad_request_error(error):
    """处理400错误"""
    return render_template('errors/400.html'), 400

# 植物资源首页 (重命名原来的index路由)
def get_beijing_time(utc_time_str='Tue, 16 Sep 2025 03:46:30 GMT'):
    """将UTC时间转换为北京时间"""
    try:
        utc_time = datetime.strptime(utc_time_str, '%a, %d %b %Y %H:%M:%S GMT')
        # UTC转北京时间（UTC+8）
        beijing_time = utc_time + timedelta(hours=8)
        return beijing_time.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return "时间格式错误"

# @main_bp.route('/plants')
# def plant_index():
#     # 获取所有筛选参数
#     search_query = request.args.get('q', '')
#     kingdom_filter = request.args.get('kingdom', '')
#     phylum_filter = request.args.get('phylum', '')
#     class_filter = request.args.get('class', '')
#     family_filter = request.args.get('family', '')
#     genus_filter = request.args.get('genus', '')
#     species_filter = request.args.get('species', '')
#     country_filter = request.args.get('country', '')
#     province_filter = request.args.get('province', '')
#     habitat_filter = request.args.get('habitat', '')
#     altitude_min_filter = request.args.get('altitude_min', '')
#     altitude_max_filter = request.args.get('altitude_max', '')
#     collection_date_start_filter = request.args.get('collection_date_start', '')
#     collection_date_end_filter = request.args.get('collection_date_end', '')
#     sequencing_status_filter = request.args.get('sequencing_status', '')
#     preservation_status_filter = request.args.get('preservation_status', '')
#     project_filter = request.args.get('project', '')
#     sort_filter = request.args.get('sort', 'created_at_desc')
    
#     # 构建查询
#     query = PlantResource.query
    
#     # 关键词搜索（搜索多个字段）
#     if search_query:
#         query = query.filter(
#             PlantResource.vernacular_name.ilike(f'%{search_query}%') |
#             PlantResource.scientific_name.ilike(f'%{search_query}%') |
#             PlantResource.description.ilike(f'%{search_query}%') |
#             PlantResource.habitat.ilike(f'%{search_query}%') |
#             PlantResource.locality.ilike(f'%{search_query}%')
#             )
    
#     # 分类筛选
#     if kingdom_filter:
#         query = query.filter(PlantResource.kingdom == kingdom_filter)
#     if phylum_filter:
#         query = query.filter(PlantResource.phylum == phylum_filter)
#     if class_filter:
#         query = query.filter(PlantResource.class_ == class_filter)
#     if family_filter:
#         query = query.filter(PlantResource.family == family_filter)
#     if genus_filter:
#         query = query.filter(PlantResource.genus == genus_filter)
#     if species_filter:
#         query = query.filter(PlantResource.species_name == species_filter)
    
#     # 地理筛选
#     if country_filter:
#         query = query.filter(PlantResource.country == country_filter)
#     if province_filter:
#         query = query.filter(PlantResource.state_province == province_filter)
    
#     # 环境筛选
#     if habitat_filter:
#         query = query.filter(PlantResource.habitat.ilike(f'%{habitat_filter}%'))
    
#     # 海拔范围筛选
#     if altitude_min_filter:
#         try:
#             query = query.filter(PlantResource.minimum_elevation_in_meters >= float(altitude_min_filter))
#         except ValueError:
#             pass
#     if altitude_max_filter:
#         try:
#             query = query.filter(PlantResource.minimum_elevation_in_meters <= float(altitude_max_filter))
#         except ValueError:
#             pass
    
#     # 时间范围筛选
#     if collection_date_start_filter:
#         try:
#             start_date = datetime.strptime(collection_date_start_filter, '%Y-%m-%d').date()
#             query = query.filter(PlantResource.event_date >= start_date)
#         except ValueError:
#             pass
#     if collection_date_end_filter:
#         try:
#             end_date = datetime.strptime(collection_date_end_filter, '%Y-%m-%d').date()
#             query = query.filter(PlantResource.event_date <= end_date)
#         except ValueError:
#             pass
    
#     # 状态筛选
#     if sequencing_status_filter:
#         query = query.filter(PlantResource.sequencing_status == sequencing_status_filter)
#     if preservation_status_filter:
#         query = query.filter(PlantResource.physical_state == preservation_status_filter)
    
#     # 项目筛选
#     if project_filter:
#         query = query.filter(PlantResource.project_name == project_filter)
    
#     # 排序
#     if sort_filter == 'created_at_desc':
#         query = query.order_by(PlantResource.created_at.desc())
#     elif sort_filter == 'created_at_asc':
#         query = query.order_by(PlantResource.created_at.asc())
#     elif sort_filter == 'name_asc':
#         query = query.order_by(PlantResource.vernacular_name.asc())
#     elif sort_filter == 'name_desc':
#         query = query.order_by(PlantResource.vernacular_name.desc())
#     elif sort_filter == 'altitude_desc':
#         query = query.order_by(PlantResource.minimum_elevation_in_meters.desc())
#     elif sort_filter == 'altitude_asc':
#         query = query.order_by(PlantResource.minimum_elevation_in_meters.asc())
    
#     # 分页
#     page = request.args.get('page', 1, type=int)
#     per_page = 20
#     pagination = query.paginate(page=page, per_page=per_page, error_out=False)
#     plants = pagination.items
    
#     # 获取筛选选项数据
#     families = db.session.query(PlantResource.family).distinct().filter(PlantResource.family.isnot(None)).order_by(PlantResource.family).all()
#     families = [f[0] for f in families if f[0]]
    
#     countries = db.session.query(PlantResource.country).distinct().filter(PlantResource.country.isnot(None)).order_by(PlantResource.country).all()
#     countries = [c[0] for c in countries if c[0]]
    
#     habitats = db.session.query(PlantResource.habitat).distinct().filter(PlantResource.habitat.isnot(None)).order_by(PlantResource.habitat).all()
#     habitats = [h[0] for h in habitats if h[0]]
    
#     kingdoms = db.session.query(PlantResource.kingdom).distinct().filter(PlantResource.kingdom.isnot(None)).order_by(PlantResource.kingdom).all()
#     kingdoms = [k[0] for k in kingdoms if k[0]]
    
#     phylums = db.session.query(PlantResource.phylum).distinct().filter(PlantResource.phylum.isnot(None)).order_by(PlantResource.phylum).all()
#     phylums = [p[0] for p in phylums if p[0]]
    
#     classes = db.session.query(PlantResource.class_).distinct().filter(PlantResource.class_.isnot(None)).order_by(PlantResource.class_).all()
#     classes = [c[0] for c in classes if c[0]]
    
#     genera = db.session.query(PlantResource.genus).distinct().filter(PlantResource.genus.isnot(None)).order_by(PlantResource.genus).all()
#     genera = [g[0] for g in genera if g[0]]
    
#     species_list = db.session.query(PlantResource.species_name).distinct().filter(PlantResource.species_name.isnot(None)).order_by(PlantResource.species_name).all()
#     species_list = [s[0] for s in species_list if s[0]]
    
#     provinces = db.session.query(PlantResource.state_province).distinct().filter(PlantResource.state_province.isnot(None)).order_by(PlantResource.state_province).all()
#     provinces = [p[0] for p in provinces if p[0]]
    
#     projects = db.session.query(PlantResource.project_name).distinct().filter(PlantResource.project_name.isnot(None)).order_by(PlantResource.project_name).all()
#     projects = [p[0] for p in projects if p[0]]
    
#     # 时间转换
#     beijing_time = get_beijing_time()
    
#     return render_template('plant_index.html',
#                          plants=plants,
#                          pagination=pagination,
#                          search_query=search_query,
#                          kingdom_filter=kingdom_filter,
#                          phylum_filter=phylum_filter,
#                          class_filter=class_filter,
#                          family_filter=family_filter,
#                          genus_filter=genus_filter,
#                          species_filter=species_filter,
#                          country_filter=country_filter,
#                          province_filter=province_filter,
#                          habitat_filter=habitat_filter,
#                          altitude_min_filter=altitude_min_filter,
#                          altitude_max_filter=altitude_max_filter,
#                          collection_date_start_filter=collection_date_start_filter,
#                          collection_date_end_filter=collection_date_end_filter,
#                          sequencing_status_filter=sequencing_status_filter,
#                          preservation_status_filter=preservation_status_filter,
#                          project_filter=project_filter,
#                          sort_filter=sort_filter,
#                          families=families,
#                          countries=countries,
#                          habitats=habitats,
#                          kingdoms=kingdoms,
#                          phylums=phylums,
#                          classes=classes,
#                          genera=genera,
#                          species_list=species_list,
#                          provinces=provinces,
#                          projects=projects,
#                          beijing_time=beijing_time)
@main_bp.route('/plants')
def plant_index():
    """植物资源首页"""
    # 原来的index函数内容，但需要将模板改为plant_index.html
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # 获取搜索参数
    search_query = request.args.get('q', '')
    family_filter = request.args.get('family', '')
    country_filter = request.args.get('country', '')
    habitat_filter = request.args.get('habitat', '')
    
    # 构建查询
    query = PlantResource.query
    
    if search_query:
        query = query.filter(
            (PlantResource.scientific_name.ilike(f'%{search_query}%')) |
            (PlantResource.vernacular_name.ilike(f'%{search_query}%')) |
            (PlantResource.family.ilike(f'%{search_query}%'))
        )
    
    if family_filter:
        query = query.filter(PlantResource.family == family_filter)
    
    if country_filter:
        query = query.filter(PlantResource.country == country_filter)
        
    if habitat_filter:
        query = query.filter(PlantResource.habitat.ilike(f'%{habitat_filter}%'))
    
    plants = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 获取筛选选项
    families = db.session.query(PlantResource.family).distinct().all()
    countries = db.session.query(PlantResource.country).distinct().all()
    habitats = db.session.query(PlantResource.habitat).distinct().all()
    
    return render_template('plant/index.html', 
                         plants=plants,
                         families=[f[0] for f in families if f[0]],
                         countries=[c[0] for c in countries if c[0]],
                         habitats=[h[0] for h in habitats if h[0]],
                         search_query=search_query,
                         family_filter=family_filter,
                         country_filter=country_filter,
                         habitat_filter=habitat_filter)

@main_bp.route('/plant/<int:id>')
def plant_detail(id):
    """植物详情页"""
    plant = PlantResource.query.get_or_404(id)
    return render_template('plant/detail.html', plant=plant)

@main_bp.route('/plant/add', methods=['GET', 'POST'])
def plant_add():
    """添加植物记录"""
    if request.method == 'POST':
        try:
            # 创建新记录
            new_plant = PlantResource(
                classification=request.form.get('classification') or None,
                kingdom=request.form.get('kingdom') or None,
                chinese_kingdom_name=request.form.get('chinese_kingdom_name') or None,
                family=request.form.get('family') or None,
                chinese_family_name=request.form.get('chinese_family_name') or None,
                genus=request.form.get('genus') or None,
                chinese_genus_name=request.form.get('chinese_genus_name') or None,
                scientific_name=request.form.get('scientific_name') or None,
                vernacular_name=request.form.get('vernacular_name') or None,
                identification_id=request.form.get('identification_id') or None,
                recorded_by=request.form.get('recorded_by') or None,
                record_number=request.form.get('record_number') or None,
                event_date=request.form.get('event_date') or None,
                identified_by=request.form.get('identified_by') or None,
                country=request.form.get('country') or None,
                state_province=request.form.get('state_province') or None,
                city=request.form.get('city') or None,
                county=request.form.get('county') or None,
                locality=request.form.get('locality') or None,
                decimal_latitude=float(request.form.get('decimal_latitude')) if request.form.get('decimal_latitude') else None,
                decimal_longitude=float(request.form.get('decimal_longitude')) if request.form.get('decimal_longitude') else None,
                minimum_elevation_in_meters=float(request.form.get('minimum_elevation_in_meters')) if request.form.get('minimum_elevation_in_meters') else None,
                habitat=request.form.get('habitat') or None,
                habit=request.form.get('habit') or None
            )
            
            db.session.add(new_plant)
            db.session.commit()
            flash('植物记录添加成功!', 'success')
            return redirect(url_for('main.plant_index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'添加植物记录时出错: {str(e)}', 'danger')
            # 重新渲染表单，保留用户输入
            return render_template('plant/add.html')
    
    return render_template('plant/add.html')

@main_bp.route('/plant/edit/<int:id>', methods=['GET', 'POST'])
def plant_edit(id):
    """编辑植物记录"""
    plant = PlantResource.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # 更新记录
            plant.classification = request.form.get('classification') or None
            plant.kingdom = request.form.get('kingdom') or None
            plant.chinese_kingdom_name = request.form.get('chinese_kingdom_name') or None
            plant.family = request.form.get('family') or None
            plant.chinese_family_name = request.form.get('chinese_family_name') or None
            plant.genus = request.form.get('genus') or None
            plant.chinese_genus_name = request.form.get('chinese_genus_name') or None
            plant.scientific_name = request.form.get('scientific_name') or None
            plant.vernacular_name = request.form.get('vernacular_name') or None
            plant.identification_id = request.form.get('identification_id') or None
            plant.recorded_by = request.form.get('recorded_by') or None
            plant.record_number = request.form.get('record_number') or None
            plant.event_date = request.form.get('event_date') or None
            plant.identified_by = request.form.get('identified_by') or None
            plant.country = request.form.get('country') or None
            plant.state_province = request.form.get('state_province') or None
            plant.city = request.form.get('city') or None
            plant.county = request.form.get('county') or None
            plant.locality = request.form.get('locality') or None
            
            # 处理数值字段
            decimal_latitude = request.form.get('decimal_latitude')
            plant.decimal_latitude = float(decimal_latitude) if decimal_latitude else None
            
            decimal_longitude = request.form.get('decimal_longitude')
            plant.decimal_longitude = float(decimal_longitude) if decimal_longitude else None
            
            min_elevation = request.form.get('minimum_elevation_in_meters')
            plant.minimum_elevation_in_meters = float(min_elevation) if min_elevation else None
            
            plant.habitat = request.form.get('habitat') or None
            plant.habit = request.form.get('habit') or None
            
            db.session.commit()
            flash('植物记录更新成功!', 'success')
            return redirect(url_for('main.plant_detail', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'更新植物记录时出错: {str(e)}', 'danger')
            # 重新渲染表单，保留用户输入
            return render_template('plant/edit.html', plant=plant)
    
    return render_template('plant/edit.html', plant=plant)

@main_bp.route('/plant/delete/<int:id>', methods=['POST'])
def plant_delete(id):
    """删除植物记录"""
    plant = PlantResource.query.get_or_404(id)
    db.session.delete(plant)
    db.session.commit()
    return redirect(url_for('main.plants'))

@main_bp.route('/api/plants')
def api_plants():
    """获取所有植物记录的API接口"""
    plants = PlantResource.query.all()
    return jsonify([plant.to_dict() for plant in plants])

@main_bp.route('/api/plants/<int:id>')
def api_plant_detail(id):
    """获取单个植物记录的API接口"""
    plant = PlantResource.query.get_or_404(id)
    return jsonify(plant.to_dict())

@main_bp.route('/api/plants/search')
def api_search_plants():
    """搜索植物记录的API接口"""
    search_query = request.args.get('q', '')
    family_filter = request.args.get('family', '')
    country_filter = request.args.get('country', '')
    habitat_filter = request.args.get('habitat', '')
    limit = request.args.get('limit', 50, type=int)
    
    # 构建查询
    query = PlantResource.query
    
    if search_query:
        query = query.filter(
            (PlantResource.scientific_name.ilike(f'%{search_query}%')) |
            (PlantResource.vernacular_name.ilike(f'%{search_query}%')) |
            (PlantResource.family.ilike(f'%{search_query}%')) |
            (PlantResource.genus.ilike(f'%{search_query}%'))
        )
    
    if family_filter:
        query = query.filter(PlantResource.family == family_filter)
    
    if country_filter:
        query = query.filter(PlantResource.country == country_filter)
        
    if habitat_filter:
        query = query.filter(PlantResource.habitat.ilike(f'%{habitat_filter}%'))
    
    plants = query.limit(limit).all()
    
    return jsonify([plant.to_dict() for plant in plants])


# 昆虫资源首页
@main_bp.route('/insects')
def insect_index():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 获取所有筛选参数
    search_query = request.args.get('q', '')
    family_filter = request.args.get('family', '')
    province_filter = request.args.get('province', '')
    collection_date_start = request.args.get('collection_date_start', '')
    collection_date_end = request.args.get('collection_date_end', '')
    
    # 构建查询
    query = InsectResource.query
    
    # 关键词搜索
    if search_query:
        query = query.filter(
            (InsectResource.chinese_name.ilike(f'%{search_query}%')) |
            (InsectResource.species_name.ilike(f'%{search_query}%')) |
            (InsectResource.family_name.ilike(f'%{search_query}%'))
        )
    
    # 科筛选
    if family_filter:
        query = query.filter(InsectResource.family_name == family_filter)
    
    # 省份筛选
    if province_filter:
        query = query.filter(InsectResource.province == province_filter)
    
    # 采集时间范围筛选
    if collection_date_start:
        try:
            start_date = datetime.strptime(collection_date_start, '%Y-%m-%d').date()
            query = query.filter(InsectResource.collection_date >= start_date)
        except ValueError:
            pass  # 忽略无效日期格式
    
    if collection_date_end:
        try:
            end_date = datetime.strptime(collection_date_end, '%Y-%m-%d').date()
            query = query.filter(InsectResource.collection_date <= end_date)
        except ValueError:
            pass  # 忽略无效日期格式
    
    # 执行查询并分页
    insects = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 获取筛选选项
    families = db.session.query(InsectResource.family_name).distinct().all()
    provinces = db.session.query(InsectResource.province).distinct().all()
    
    # 获取总记录数
    total_count = InsectResource.query.count()
    
    return render_template('insect/index.html', 
                         insects=insects,
                         families=[f[0] for f in families if f[0]],
                         provinces=[p[0] for p in provinces if p[0]],
                         search_query=search_query,
                         family_filter=family_filter,
                         province_filter=province_filter,
                         total_count=total_count)

# 昆虫详情页
@main_bp.route('/insect/<int:id>')
def insect_detail(id):
    """昆虫详情页"""
    insect = InsectResource.query.get_or_404(id)
    return render_template('insect/detail.html', insect=insect)

# 添加昆虫记录
@main_bp.route('/insect/add', methods=['GET', 'POST'])
def insect_add():
    """添加昆虫记录"""
    if request.method == 'POST':
        try:
            # 创建新记录
            new_insect = InsectResource(
                serial_number=request.form.get('serial_number') or None,
                leiqun=request.form.get('leiqun') or None,
                sequencing_status=request.form.get('sequencing_status') or None,
                original_id=request.form.get('original_id') or None,
                chinese_name=request.form.get('chinese_name') or None,
                phylum=request.form.get('phylum') or None,
                phylum_name=request.form.get('phylum_name') or None,
                class_=request.form.get('class_') or None,
                class_name=request.form.get('class_name') or None,
                order=request.form.get('order') or None,
                order_name=request.form.get('order_name') or None,
                chinese_family_name=request.form.get('chinese_family_name') or None,
                family_name=request.form.get('family_name') or None,
                genus_name=request.form.get('genus_name') or None,
                species_name=request.form.get('species_name') or None,
                infraspecies_name=request.form.get('infraspecies_name') or None,
                citation1=request.form.get('citation1') or None,
                citation2=request.form.get('citation2') or None,
                resource_code=request.form.get('resource_code') or None,
                country=request.form.get('country') or None,
                province=request.form.get('province') or None,
                province_code=request.form.get('province_code') or None,
                county=request.form.get('county') or None,
                locality=request.form.get('locality') or None,
                longitude=float(request.form.get('longitude')) if request.form.get('longitude') else None,
                latitude=float(request.form.get('latitude')) if request.form.get('latitude') else None,
                altitude=float(request.form.get('altitude')) if request.form.get('altitude') else None,
                description=request.form.get('description') or None,
                habitat=request.form.get('habitat') or None,
                host=request.form.get('host') or None,
                image_url=request.form.get('image_url') or None,
                record_url=request.form.get('record_url') or None,
                preservation_institution=request.form.get('preservation_institution') or None,
                institution_code=request.form.get('institution_code') or None,
                collector=request.form.get('collector') or None,
                collection_date=datetime.strptime(request.form.get('collection_date'), '%Y-%m-%d').date() if request.form.get('collection_date') else None,
                collection_number=request.form.get('collection_number') or None,
                specimen_number=request.form.get('specimen_number') or None,
                identifier=request.form.get('identifier') or None,
                identification_date=datetime.strptime(request.form.get('identification_date'), '%Y-%m-%d').date() if request.form.get('identification_date') else None,
                specimen_attribute=request.form.get('specimen_attribute') or None,
                preservation_method=request.form.get('preservation_method') or None,
                physical_state=request.form.get('physical_state') or None,
                sharing_method=request.form.get('sharing_method') or None,
                access_method=request.form.get('access_method') or None,
                literature=request.form.get('literature') or None,
                contact_person=request.form.get('contact_person') or None,
                institution_address=request.form.get('institution_address') or None,
                postcode=request.form.get('postcode') or None,
                phone=request.form.get('phone') or None,
                email=request.form.get('email') or None,
                project_name=request.form.get('project_name') or None,
                project_code=request.form.get('project_code') or None,
                report_date=datetime.strptime(request.form.get('report_date'), '%Y-%m-%d').date() if request.form.get('report_date') else None,
                sampling_point=request.form.get('sampling_point') or None,
                gene_code=request.form.get('gene_code') or None,
                gene_name=request.form.get('gene_name') or None,
                gene_description=request.form.get('gene_description') or None,
                gene_alias=request.form.get('gene_alias') or None,
                sequencing_date=datetime.strptime(request.form.get('sequencing_date'), '%Y-%m-%d').date() if request.form.get('sequencing_date') else None,
                sequencer=request.form.get('sequencer') or None,
                project_task_code=request.form.get('project_task_code') or None
            )
            
            db.session.add(new_insect)
            db.session.commit()
            flash('昆虫记录添加成功!', 'success')
            return redirect(url_for('main.insect_index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'添加昆虫记录时出错: {str(e)}', 'danger')
            # 重新渲染表单，保留用户输入
            return render_template('insect/add.html')
    
    return render_template('insect/add.html')

# 编辑昆虫记录
@main_bp.route('/insect/edit/<int:id>', methods=['GET', 'POST'])
def insect_edit(id):
    """编辑昆虫记录"""
    insect = InsectResource.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # 更新记录
            insect.serial_number = request.form.get('serial_number') or None
            insect.leiqun = request.form.get('leiqun') or None
            insect.sequencing_status = request.form.get('sequencing_status') or None
            insect.original_id = request.form.get('original_id') or None
            insect.chinese_name = request.form.get('chinese_name') or None
            insect.phylum = request.form.get('phylum') or None
            insect.phylum_name = request.form.get('phylum_name') or None
            insect.class_ = request.form.get('class_') or None
            insect.class_name = request.form.get('class_name') or None
            insect.order = request.form.get('order') or None
            insect.order_name = request.form.get('order_name') or None
            insect.chinese_family_name = request.form.get('chinese_family_name') or None
            insect.family_name = request.form.get('family_name') or None
            insect.genus_name = request.form.get('genus_name') or None
            insect.species_name = request.form.get('species_name') or None
            insect.infraspecies_name = request.form.get('infraspecies_name') or None
            insect.citation1 = request.form.get('citation1') or None
            insect.citation2 = request.form.get('citation2') or None
            insect.resource_code = request.form.get('resource_code') or None
            insect.country = request.form.get('country') or None
            insect.province = request.form.get('province') or None
            insect.province_code = request.form.get('province_code') or None
            insect.county = request.form.get('county') or None
            insect.locality = request.form.get('locality') or None
            
            # 处理数值字段
            longitude = request.form.get('longitude')
            insect.longitude = float(longitude) if longitude else None
            
            latitude = request.form.get('latitude')
            insect.latitude = float(latitude) if latitude else None
            
            altitude = request.form.get('altitude')
            insect.altitude = float(altitude) if altitude else None
            
            insect.description = request.form.get('description') or None
            insect.habitat = request.form.get('habitat') or None
            insect.host = request.form.get('host') or None
            insect.image_url = request.form.get('image_url') or None
            insect.record_address = request.form.get('record_address') or None
            insect.preservation_institution = request.form.get('preservation_institution') or None
            insect.institution_code = request.form.get('institution_code') or None
            insect.collector = request.form.get('collector') or None
            
            # 处理日期字段
            collection_date = request.form.get('collection_date')
            if collection_date:
                insect.collection_date = datetime.strptime(collection_date, '%Y-%m-%d').date()
            else:
                insect.collection_date = None
                
            insect.collection_number = request.form.get('collection_number') or None
            insect.specimen_number = request.form.get('specimen_number') or None
            insect.identifier = request.form.get('identifier') or None
            
            identification_date = request.form.get('identification_date')
            if identification_date:
                insect.identification_date = datetime.strptime(identification_date, '%Y-%m-%d').date()
            else:
                insect.identification_date = None
                
            insect.specimen_attribute = request.form.get('specimen_attribute') or None
            insect.preservation_method = request.form.get('preservation_method') or None
            insect.physical_state = request.form.get('physical_state') or None
            insect.sharing_method = request.form.get('sharing_method') or None
            insect.access_method = request.form.get('access_method') or None
            insect.literature = request.form.get('literature') or None
            insect.contact_person = request.form.get('contact_person') or None
            insect.institution_address = request.form.get('institution_address') or None
            insect.postcode = request.form.get('postcode') or None
            insect.phone = request.form.get('phone') or None
            insect.email = request.form.get('email') or None
            insect.project_name = request.form.get('project_name') or None
            insect.project_code = request.form.get('project_code') or None
            
            report_date = request.form.get('report_date')
            if report_date:
                insect.report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
            else:
                insect.report_date = None
                
            insect.sampling_point = request.form.get('sampling_point') or None
            insect.gene_code = request.form.get('gene_code') or None
            insect.gene_name = request.form.get('gene_name') or None
            insect.gene_description = request.form.get('gene_description') or None
            insect.gene_alias = request.form.get('gene_alias') or None
            
            sequencing_date = request.form.get('sequencing_date')
            if sequencing_date:
                insect.sequencing_date = datetime.strptime(sequencing_date, '%Y-%m-%d').date()
            else:
                insect.sequencing_date = None
                
            insect.sequencer = request.form.get('sequencer') or None
            insect.project_task_code = request.form.get('project_task_code') or None
            
            db.session.commit()
            flash('昆虫记录更新成功!', 'success')
            return redirect(url_for('main.insect_detail', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'更新昆虫记录时出错: {str(e)}', 'danger')
            # 重新渲染表单，保留用户输入
            return render_template('insect/edit.html', insect=insect)
    
    return render_template('insect/edit.html', insect=insect)

# 删除昆虫记录
@main_bp.route('/insect/delete/<int:id>', methods=['POST'])
def insect_delete(id):
    """删除昆虫记录"""
    insect = InsectResource.query.get_or_404(id)
    db.session.delete(insect)
    db.session.commit()
    flash('昆虫记录已删除!', 'success')
    return redirect(url_for('main.insect_index'))