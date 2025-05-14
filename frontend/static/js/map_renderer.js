/**
 * 地图渲染器模块
 * 负责渲染游戏地图、城市和铁路网络
 */

class MapRenderer {
    constructor(containerId = 'map-container') {
        this.container = document.getElementById(containerId);
        this.canvas = null;
        this.ctx = null;
        this.width = 0;
        this.height = 0;
        this.scale = 1.0;
        this.offsetX = 0;
        this.offsetY = 0;
        this.isDragging = false;
        this.lastMouseX = 0;
        this.lastMouseY = 0;
        this.mapData = null;
        this.cities = [];
        this.railways = [];
        this.selectedCity = null;
        this.selectedRailway = null;
        
        // 初始化
        this.initialize();
    }
    
    /**
     * 初始化地图渲染器
     */
    initialize() {
        // 创建画布
        this.canvas = document.createElement('canvas');
        this.container.innerHTML = '';
        this.container.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');
        
        // 设置画布大小
        this.resize();
        
        // 添加事件监听器
        window.addEventListener('resize', this.resize.bind(this));
        this.canvas.addEventListener('mousedown', this.onMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.onMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.onMouseUp.bind(this));
        this.canvas.addEventListener('wheel', this.onWheel.bind(this));
        
        // 添加地图控制按钮事件
        const zoomInBtn = document.getElementById('zoom-in-btn');
        const zoomOutBtn = document.getElementById('zoom-out-btn');
        const centerMapBtn = document.getElementById('center-map-btn');
        
        if (zoomInBtn) zoomInBtn.addEventListener('click', () => this.zoom(1.2));
        if (zoomOutBtn) zoomOutBtn.addEventListener('click', () => this.zoom(0.8));
        if (centerMapBtn) centerMapBtn.addEventListener('click', () => this.centerMap());
        
        // 注册WebSocket事件处理器
        if (typeof wsManager !== 'undefined') {
            wsManager.on('map_data', this.handleMapData.bind(this));
            wsManager.on('city_data', this.handleCityData.bind(this));
            wsManager.on('railway_data', this.handleRailwayData.bind(this));
        }
    }
    
    /**
     * 调整画布大小
     */
    resize() {
        if (!this.container || !this.canvas) return;
        
        // 获取容器大小
        const rect = this.container.getBoundingClientRect();
        this.width = rect.width;
        this.height = rect.height;
        
        // 设置画布大小
        this.canvas.width = this.width;
        this.canvas.height = this.height;
        
        // 重新渲染
        this.render();
    }
    
    /**
     * 处理地图数据
     * @param {Object} data 地图数据
     */
    handleMapData(data) {
        this.mapData = data;
        this.render();
    }
    
    /**
     * 处理城市数据
     * @param {Object} data 城市数据
     */
    handleCityData(data) {
        this.cities = data.cities || [];
        this.render();
    }
    
    /**
     * 处理铁路数据
     * @param {Object} data 铁路数据
     */
    handleRailwayData(data) {
        this.railways = data.railways || [];
        this.render();
    }
    
    /**
     * 渲染地图
     */
    render() {
        if (!this.ctx) return;
        
        // 清空画布
        this.ctx.clearRect(0, 0, this.width, this.height);
        
        // 绘制背景
        this.drawBackground();
        
        // 绘制地形
        this.drawTerrain();
        
        // 绘制铁路
        this.drawRailways();
        
        // 绘制城市
        this.drawCities();
        
        // 绘制UI元素
        this.drawUI();
    }
    
    /**
     * 绘制背景
     */
    drawBackground() {
        this.ctx.fillStyle = '#e6f7ff'; // 浅蓝色背景
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        // 绘制网格
        this.ctx.strokeStyle = '#ccc';
        this.ctx.lineWidth = 0.5;
        
        const gridSize = 50 * this.scale;
        const startX = this.offsetX % gridSize;
        const startY = this.offsetY % gridSize;
        
        // 绘制垂直线
        for (let x = startX; x < this.width; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.height);
            this.ctx.stroke();
        }
        
        // 绘制水平线
        for (let y = startY; y < this.height; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.width, y);
            this.ctx.stroke();
        }
    }
    
    /**
     * 绘制地形
     */
    drawTerrain() {
        if (!this.mapData || !this.mapData.terrain) return;
        
        // TODO: 实现地形渲染
        // 这里可以根据地形数据绘制山脉、河流、森林等
    }
    
    /**
     * 绘制城市
     */
    drawCities() {
        if (!this.cities || this.cities.length === 0) {
            // 如果没有城市数据，绘制一些示例城市
            this.drawSampleCities();
            return;
        }
        
        this.cities.forEach(city => {
            const x = city.x * this.scale + this.offsetX;
            const y = city.y * this.scale + this.offsetY;
            const radius = 5 + (city.population / 10000) * this.scale;
            const isSelected = this.selectedCity && this.selectedCity.id === city.id;
            
            // 绘制城市圆形
            this.ctx.beginPath();
            this.ctx.arc(x, y, radius, 0, Math.PI * 2);
            this.ctx.fillStyle = isSelected ? '#ff9900' : '#3498db';
            this.ctx.fill();
            this.ctx.strokeStyle = '#2980b9';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            // 绘制城市名称
            this.ctx.font = `${12 * this.scale}px Arial`;
            this.ctx.fillStyle = '#333';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'bottom';
            this.ctx.fillText(city.name, x, y - radius - 5);
            
            // 绘制人口信息
            this.ctx.font = `${10 * this.scale}px Arial`;
            this.ctx.fillStyle = '#666';
            this.ctx.textBaseline = 'top';
            this.ctx.fillText(`${Math.floor(city.population / 1000)}k`, x, y + radius + 5);
        });
    }
    
    /**
     * 绘制示例城市（当没有真实数据时）
     */
    drawSampleCities() {
        const sampleCities = [
            { id: 1, name: '北京', x: 100, y: 100, population: 2000000 },
            { id: 2, name: '上海', x: 300, y: 200, population: 1800000 },
            { id: 3, name: '广州', x: 200, y: 300, population: 1500000 },
            { id: 4, name: '深圳', x: 250, y: 350, population: 1200000 },
            { id: 5, name: '成都', x: 150, y: 250, population: 1000000 }
        ];
        
        sampleCities.forEach(city => {
            const x = city.x * this.scale + this.offsetX;
            const y = city.y * this.scale + this.offsetY;
            const radius = 5 + (city.population / 500000) * this.scale;
            
            // 绘制城市圆形
            this.ctx.beginPath();
            this.ctx.arc(x, y, radius, 0, Math.PI * 2);
            this.ctx.fillStyle = '#3498db';
            this.ctx.fill();
            this.ctx.strokeStyle = '#2980b9';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            // 绘制城市名称
            this.ctx.font = `${12 * this.scale}px Arial`;
            this.ctx.fillStyle = '#333';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'bottom';
            this.ctx.fillText(city.name, x, y - radius - 5);
        });
    }
    
    /**
     * 绘制铁路
     */
    drawRailways() {
        if (!this.railways || this.railways.length === 0) {
            // 如果没有铁路数据，绘制一些示例铁路
            this.drawSampleRailways();
            return;
        }
        
        this.railways.forEach(railway => {
            const startX = railway.startX * this.scale + this.offsetX;
            const startY = railway.startY * this.scale + this.offsetY;
            const endX = railway.endX * this.scale + this.offsetX;
            const endY = railway.endY * this.scale + this.offsetY;
            const isSelected = this.selectedRailway && this.selectedRailway.id === railway.id;
            
            // 绘制铁路线
            this.ctx.beginPath();
            this.ctx.moveTo(startX, startY);
            
            if (railway.controlPoints && railway.controlPoints.length > 0) {
                // 如果有控制点，绘制贝塞尔曲线
                railway.controlPoints.forEach((point, index) => {
                    const cpX = point.x * this.scale + this.offsetX;
                    const cpY = point.y * this.scale + this.offsetY;
                    
                    if (index === 0) {
                        this.ctx.quadraticCurveTo(cpX, cpY, endX, endY);
                    } else {
                        // 多个控制点时使用更复杂的曲线
                        // 这里简化处理
                        this.ctx.lineTo(cpX, cpY);
                    }
                });
                
                if (railway.controlPoints.length === 0) {
                    this.ctx.lineTo(endX, endY);
                }
            } else {
                // 没有控制点，直接绘制直线
                this.ctx.lineTo(endX, endY);
            }
            
            this.ctx.strokeStyle = isSelected ? '#ff9900' : '#e74c3c';
            this.ctx.lineWidth = isSelected ? 4 : 3;
            this.ctx.stroke();
            
            // 绘制铁路名称
            if (railway.name) {
                const midX = (startX + endX) / 2;
                const midY = (startY + endY) / 2;
                
                this.ctx.font = `${11 * this.scale}px Arial`;
                this.ctx.fillStyle = '#333';
                this.ctx.textAlign = 'center';
                this.ctx.textBaseline = 'middle';
                
                // 添加白色背景使文字更清晰
                const textWidth = this.ctx.measureText(railway.name).width;
                this.ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
                this.ctx.fillRect(midX - textWidth / 2 - 2, midY - 8, textWidth + 4, 16);
                
                this.ctx.fillStyle = '#333';
                this.ctx.fillText(railway.name, midX, midY);
            }
        });
    }
    
    /**
     * 绘制示例铁路（当没有真实数据时）
     */
    drawSampleRailways() {
        const sampleRailways = [
            { id: 1, name: '京沪线', startX: 100, startY: 100, endX: 300, endY: 200 },
            { id: 2, name: '广深线', startX: 200, startY: 300, endX: 250, endY: 350 },
            { id: 3, name: '成渝线', startX: 150, startY: 250, endX: 100, endY: 300 }
        ];
        
        sampleRailways.forEach(railway => {
            const startX = railway.startX * this.scale + this.offsetX;
            const startY = railway.startY * this.scale + this.offsetY;
            const endX = railway.endX * this.scale + this.offsetX;
            const endY = railway.endY * this.scale + this.offsetY;
            
            // 绘制铁路线
            this.ctx.beginPath();
            this.ctx.moveTo(startX, startY);
            this.ctx.lineTo(endX, endY);
            this.ctx.strokeStyle = '#e74c3c';
            this.ctx.lineWidth = 3;
            this.ctx.stroke();
            
            // 绘制铁路名称
            const midX = (startX + endX) / 2;
            const midY = (startY + endY) / 2;
            
            this.ctx.font = `${11 * this.scale}px Arial`;
            this.ctx.fillStyle = '#333';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            
            // 添加白色背景使文字更清晰
            const textWidth = this.ctx.measureText(railway.name).width;
            this.ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
            this.ctx.fillRect(midX - textWidth / 2 - 2, midY - 8, textWidth + 4, 16);
            
            this.ctx.fillStyle = '#333';
            this.ctx.fillText(railway.name, midX, midY);
        });
    }
    
    /**
     * 绘制UI元素
     */
    drawUI() {
        // 绘制比例尺
        this.drawScale();
        
        // 绘制坐标信息
        this.drawCoordinates();
    }
    
    /**
     * 绘制比例尺
     */
    drawScale() {
        const scaleLength = 100 * this.scale;
        const x = 20;
        const y = this.height - 20;
        
        this.ctx.beginPath();
        this.ctx.moveTo(x, y);
        this.ctx.lineTo(x + scaleLength, y);
        this.ctx.strokeStyle = '#333';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
        
        // 绘制刻度
        this.ctx.beginPath();
        this.ctx.moveTo(x, y - 5);
        this.ctx.lineTo(x, y + 5);
        this.ctx.moveTo(x + scaleLength, y - 5);
        this.ctx.lineTo(x + scaleLength, y + 5);
        this.ctx.stroke();
        
        // 绘制文字
        this.ctx.font = '12px Arial';
        this.ctx.fillStyle = '#333';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'top';
        this.ctx.fillText('100 km', x + scaleLength / 2, y + 8);
    }
    
    /**
     * 绘制坐标信息
     */
    drawCoordinates() {
        const x = this.width - 10;
        const y = this.height - 10;
        
        this.ctx.font = '12px Arial';
        this.ctx.fillStyle = '#333';
        this.ctx.textAlign = 'right';
        this.ctx.textBaseline = 'bottom';
        this.ctx.fillText(`缩放: ${this.scale.toFixed(2)}x`, x, y);
    }
    
    /**
     * 鼠标按下事件处理
     * @param {MouseEvent} event 鼠标事件
     */
    onMouseDown(event) {
        this.isDragging = true;
        this.lastMouseX = event.clientX;
        this.lastMouseY = event.clientY;
        
        // 检查是否点击了城市或铁路
        this.checkSelection(event.clientX, event.clientY);
    }
    
    /**
     * 鼠标移动事件处理
     * @param {MouseEvent} event 鼠标事件
     */
    onMouseMove(event) {
        if (!this.isDragging) return;
        
        const deltaX = event.clientX - this.lastMouseX;
        const deltaY = event.clientY - this.lastMouseY;
        
        this.offsetX += deltaX;
        this.offsetY += deltaY;
        
        this.lastMouseX = event.clientX;
        this.lastMouseY = event.clientY;
        
        this.render();
    }
    
    /**
     * 鼠标释放事件处理
     * @param {MouseEvent} event 鼠标事件
     */
    onMouseUp(event) {
        this.isDragging = false;
    }
    
    /**
     * 鼠标滚轮事件处理
     * @param {WheelEvent} event 滚轮事件
     */
    onWheel(event) {
        event.preventDefault();
        
        const zoomFactor = event.deltaY > 0 ? 0.9 : 1.1;
        this.zoom(zoomFactor, event.clientX, event.clientY);
    }
    
    /**
     * 缩放地图
     * @param {number} factor 缩放因子
     * @param {number} centerX 缩放中心X坐标
     * @param {number} centerY 缩放中心Y坐标
     */
    zoom(factor, centerX = this.width / 2, centerY = this.height / 2) {
        // 计算鼠标位置相对于地图的偏移
        const mouseXRelToMap = centerX - this.offsetX;
        const mouseYRelToMap = centerY - this.offsetY;
        
        // 应用缩放
        const oldScale = this.scale;
        this.scale *= factor;
        
        // 限制缩放范围
        this.scale = Math.max(0.2, Math.min(5.0, this.scale));
        
        // 调整偏移以保持鼠标位置不变
        this.offsetX = centerX - mouseXRelToMap * (this.scale / oldScale);
        this.offsetY = centerY - mouseYRelToMap * (this.scale / oldScale);
        
        this.render();
    }
    
    /**
     * 居中地图
     */
    centerMap() {
        this.offsetX = this.width / 2;
        this.offsetY = this.height / 2;
        this.scale = 1.0;
        this.render();
    }
    
    /**
     * 检查选择
     * @param {number} mouseX 鼠标X坐标
     * @param {number} mouseY 鼠标Y坐标
     */
    checkSelection(mouseX, mouseY) {
        // 检查是否点击了城市
        let selectedCity = null;
        
        if (this.cities && this.cities.length > 0) {
            for (let i = this.cities.length - 1; i >= 0; i--) {
                const city = this.cities[i];
                const x = city.x * this.scale + this.offsetX;
                const y = city.y * this.scale + this.offsetY;
                const radius = 5 + (city.population / 10000) * this.scale;
                
                const distance = Math.sqrt(Math.pow(mouseX - x, 2) + Math.pow(mouseY - y, 2));
                
                if (distance <= radius) {
                    selectedCity = city;
                    break;
                }
            }
        } else {
            // 使用示例城市数据
            const sampleCities = [
                { id: 1, name: '北京', x: 100, y: 100, population: 2000000 },
                { id: 2, name: '上海', x: 300, y: 200, population: 1800000 },
                { id: 3, name: '广州', x: 200, y: 300, population: 1500000 },
                { id: 4, name: '深圳', x: 250, y: 350, population: 1200000 },
                { id: 5, name: '成都', x: 150, y: 250, population: 1000000 }
            ];
            
            for (let i = sampleCities.length - 1; i >= 0; i--) {
                const city = sampleCities[i];
                const x = city.x * this.scale + this.offsetX;
                const y = city.y * this.scale + this.offsetY;
                const radius = 5 + (city.population / 500000) * this.scale;
                
                const distance = Math.sqrt(Math.pow(mouseX - x, 2) + Math.pow(mouseY - y, 2));
                
                if (distance <= radius) {
                    selectedCity = city;
                    break;
                }
            }
        }
        
        // 更新选中的城市
        if (selectedCity !== this.selectedCity) {
            this.selectedCity = selectedCity;
            this.render();
            
            // 触发城市选择事件
            if (selectedCity && typeof window.onCitySelected === 'function') {
                window.onCitySelected(selectedCity);
            }
        }
        
        // TODO: 实现铁路选择
    }
}

// 创建地图渲染器实例
const mapRenderer = new MapRenderer();

// 导出地图渲染器
window.mapRenderer = mapRenderer;