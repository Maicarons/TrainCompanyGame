# 地图渲染器单元测试

import unittest
from unittest.mock import MagicMock, patch
import json

# 由于前端代码需要在浏览器环境中运行，我们需要模拟DOM环境
class MockCanvas:
    def getContext(self, context_type):
        return MagicMock()

class MockDocument:
    def getElementById(self, id):
        element = MagicMock()
        element.innerHTML = ''
        element.appendChild = MagicMock()
        return element
    
    def createElement(self, element_type):
        if element_type == 'canvas':
            return MockCanvas()
        return MagicMock()

class TestMapRenderer(unittest.TestCase):
    """测试地图渲染器"""
    
    def setUp(self):
        """测试前准备"""
        # 模拟浏览器环境
        self.original_document = None
        self.original_window = None
        
        # 模拟地图数据
        self.map_data = {
            "terrain": [[0, 0, 1], [0, 2, 1], [1, 1, 0]],
            "cities": [
                {"id": 1, "name": "城市A", "x": 100, "y": 100, "population": 500000, "type": "industrial"},
                {"id": 2, "name": "城市B", "x": 300, "y": 200, "population": 300000, "type": "commercial"}
            ],
            "railways": [
                {"id": 1, "from_city": 1, "to_city": 2, "path": [[100, 100], [200, 150], [300, 200]], "length": 250}
            ]
        }
    
    @patch('frontend.static.js.map_renderer.document', MockDocument())
    @patch('frontend.static.js.map_renderer.window', MagicMock())
    def test_map_initialization(self):
        """测试地图初始化"""
        # 导入地图渲染器类（在打补丁后导入）
        from frontend.static.js.map_renderer import MapRenderer
        
        # 创建地图渲染器实例
        renderer = MapRenderer('map-container')
        
        # 验证初始化属性
        self.assertIsNotNone(renderer.canvas)
        self.assertIsNotNone(renderer.ctx)
        self.assertEqual(renderer.scale, 1.0)
        self.assertEqual(renderer.offsetX, 0)
        self.assertEqual(renderer.offsetY, 0)
        self.assertFalse(renderer.isDragging)
    
    @patch('frontend.static.js.map_renderer.document', MockDocument())
    @patch('frontend.static.js.map_renderer.window', MagicMock())
    def test_load_map_data(self):
        """测试加载地图数据"""
        # 导入地图渲染器类
        from frontend.static.js.map_renderer import MapRenderer
        
        # 创建地图渲染器实例
        renderer = MapRenderer('map-container')
        
        # 加载地图数据
        renderer.loadMapData(self.map_data)
        
        # 验证数据是否正确加载
        self.assertEqual(renderer.mapData, self.map_data)
        self.assertEqual(len(renderer.cities), 2)
        self.assertEqual(len(renderer.railways), 1)
    
    @patch('frontend.static.js.map_renderer.document', MockDocument())
    @patch('frontend.static.js.map_renderer.window', MagicMock())
    def test_city_selection(self):
        """测试城市选择功能"""
        # 导入地图渲染器类
        from frontend.static.js.map_renderer import MapRenderer
        
        # 创建地图渲染器实例
        renderer = MapRenderer('map-container')
        renderer.loadMapData(self.map_data)
        
        # 选择城市
        city = renderer.cities[0]
        renderer.selectCity(city)
        
        # 验证选择状态
        self.assertEqual(renderer.selectedCity, city)
        
        # 取消选择
        renderer.clearSelection()
        self.assertIsNone(renderer.selectedCity)
    
    @patch('frontend.static.js.map_renderer.document', MockDocument())
    @patch('frontend.static.js.map_renderer.window', MagicMock())
    def test_map_zooming(self):
        """测试地图缩放功能"""
        # 导入地图渲染器类
        from frontend.static.js.map_renderer import MapRenderer
        
        # 创建地图渲染器实例
        renderer = MapRenderer('map-container')
        
        # 记录初始缩放级别
        initial_scale = renderer.scale
        
        # 放大地图
        renderer.zoomIn()
        self.assertGreater(renderer.scale, initial_scale)
        
        # 缩小地图
        renderer.zoomOut()
        self.assertEqual(renderer.scale, initial_scale)

if __name__ == '__main__':
    unittest.main()