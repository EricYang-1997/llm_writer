import React, { useEffect,useState } from 'react';
import {  InputNumber,Button, Form, Input, Select, Space, Card,  Divider ,Flex} from 'antd';

import {  PlusOutlined, SaveOutlined,DeleteOutlined } from '@ant-design/icons';
import { graphStore } from '../../store/graphStore';

const { Option } = Select;

const NodeCreator = () => {
  const [form] = Form.useForm();
  const [attributes, setAttributes] = useState([]);
  const [localSelectedNode, setLocalSelectedNode] = useState(null)

  useEffect(() => {
    const handleNodeClick = (nodeData) => {
      console.log('Node clicked in A component:', nodeData);
      setLocalSelectedNode(nodeData);  // 修正：应该是 setLocalSelectedNode
      
      // 将节点数据填充到表单中
      if (nodeData) {
        form.setFieldsValue({
          name: nodeData.data.name || nodeData.id,  // 修正：根据实际数据结构
          level:nodeData.data.level,
          label: nodeData.data.label,
          description:nodeData.data.description,
          status: nodeData.data.status,
          content: nodeData.data.content,
        });
        
        // 设置属性
        if (nodeData.attributes) {
          setAttributes(nodeData.attributes);
        }
      }
    };

    // 订阅事件
    graphStore.on('nodeClick', handleNodeClick);
    return () => {
      graphStore.off('nodeClick', handleNodeClick);
    };
  }, [form]);

  const handleAddAttribute = () => {
    setAttributes([...attributes, { key: '', value: '', id: Date.now() }]);
  };

  const handleAttributeChange = (index, field, value) => {
    const newAttributes = [...attributes];
    newAttributes[index][field] = value;
    setAttributes(newAttributes);
  };

  const handleRemoveAttribute = (index) => {
    const newAttributes = attributes.filter((_, i) => i !== index);
    setAttributes(newAttributes);
  };

  // 修改保存函数，如果是更新模式则调用更新方法
  const handleSave = () => {
    form.validateFields().then(values => {
      const nodeData = {
        id: values.name, // 使用 name 作为 id
        label: values.label,
        name: values.name,
        status: values.status,
        content: values.content,
        level: values.level,
        description: values.description,
        attributes: attributes.filter(attr => attr.key && attr.value)
      };

      graphStore.createOrUpdateNode(nodeData);
    })
  };
  const handleRemove=()=>{
        form.validateFields().then(values => {
      const nodeData = {
        id: values.name, // 使用 name 作为 id
        label: values.label,
        name: values.name,
        status: values.status,
        content: values.content,
        level: values.level,
        description: values.description,
        attributes: attributes.filter(attr => attr.key && attr.value)
      };

      graphStore.removeNode(nodeData);

    })
  }
  return (
<Card>
  <Form form={form} layout="horizontal">

    <Form.Item label="名称" name="name" rules={[{ required: true }]} style={{ display: 'inline-block', width: 'calc(50% - 8px)', marginRight: '16px' }}>
      <Input placeholder="节点 名称" />
    </Form.Item>

    <Form.Item label="层级" name="level" rules={[{ required: true }]} style={{ display: 'inline-block', width: 'calc(50% - 8px)' }}>
      <InputNumber 
        placeholder="输入 层级" 
        min={1}
        style={{ width: '100%' }}
      />
    </Form.Item>

    <Form.Item label="标签" name="label" rules={[{ required: true }]} style={{ display: 'inline-block', width: 'calc(50% - 8px)', marginRight: '16px' }}>
      <Select placeholder="选择 标签">
        <Option value="大纲">大纲</Option>
        <Option value="细纲">细纲</Option>
        <Option value="前幕">前幕</Option>
        <Option value="中幕">中幕</Option>
        <Option value="人物">人物</Option>
        <Option value="物品">物品</Option>
        <Option value="地点">地点</Option>
      </Select>
    </Form.Item>

    <Form.Item label="状态" name="status" rules={[{ required: true }]} style={{ display: 'inline-block', width: 'calc(50% - 8px)' }}>
      <Select placeholder="选择 类型">
        <Option value="启用">启用</Option>
        <Option value="停用">停用</Option>
        <Option value="反例">反例</Option>
        <Option value="示例">示例</Option>
      </Select>
    </Form.Item>

    <Form.Item label="描述" name="description" >
      <Input.TextArea 
        rows={1} 
        placeholder="输入 节点描述" 
      />
    </Form.Item>

    <Form.Item label="内容" name="content" >
      <Input.TextArea rows={4} placeholder="输入 主要内容" />
    </Form.Item>

    <Form.Item label="属性">
      <Space direction="vertical" style={{ width: '100%' }}>
        {attributes.map((attr, index) => (
          <Space key={attr.id}>
            <Input
              value={attr.key}
              onChange={(e) => handleAttributeChange(index, 'key', e.target.value)}
              placeholder="属性"
              style={{ width: 150 }}
            />
            <Input
              value={attr.value}
              onChange={(e) => handleAttributeChange(index, 'value', e.target.value)}
              placeholder="值"
              style={{ width: 200 }}
            />
            <Button
              type="text"
              danger
              onClick={() => handleRemoveAttribute(index)}
            >
              去掉
            </Button>
          </Space>
        ))}
        <Button 
          type="dashed" 
          onClick={handleAddAttribute}
          icon={<PlusOutlined />}
        >
          添加 属性
        </Button>
      </Space>
    </Form.Item>
  </Form>
  
  <Divider />
  <Flex wrap gap="small" className="site-button-ghost-wrapper">
    <Button 
      type="primary" 
      icon={<SaveOutlined />}
      onClick={handleSave}
    >
      {localSelectedNode ? '更新节点' : '创建节点'}
    </Button>
    {localSelectedNode && (
      <Button 
        type="primary" 
        danger
        icon={<DeleteOutlined />}  
        onClick={handleRemove}     
      >
        移除节点
      </Button>
    )}
  </Flex>
</Card>
  );
};

export default NodeCreator;