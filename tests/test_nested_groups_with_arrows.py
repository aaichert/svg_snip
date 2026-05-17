"""
Test nested Group rendering with declared SVG definitions (arrow markers).

Verifies that when a utility function returns a Group containing arrows,
the arrow marker definitions are properly collected into the final <defs> block.
"""

from svg_snip.Composer import Composer, Group, comment
from svg_snip.Elements import arrow, line


def draw_coordinate_axes(**kwargs):
    """
    Utility that returns a Group with multiple arrows.
    Each arrow declares marker definitions that must be included in final SVG.
    """
    group = Group()
    group.add(comment, text="Start of Coordinate Axes")
    
    # Add three arrows with different markers
    group.add(arrow, x1=10, y1=10, x2=100, y2=10, stroke='red', head='arrow-small', tail=None)
    group.add(arrow, x1=10, y1=10, x2=10, y2=100, stroke='green', head='arrow-large', tail='circle')
    group.add(arrow, x1=10, y1=10, x2=100, y2=100, stroke='blue', head='star', tail='star')
    
    return group


def test_nested_group_arrow_definitions():
    """Test that arrow marker definitions are collected from nested groups."""
    svg = Composer((200, 200))
    svg.add(draw_coordinate_axes)
    
    rendered = svg.render()
    
    # Verify the SVG contains the nested comments
    assert '<!-- Start of Coordinate Axes -->' in rendered
    
    # Verify all arrow marker definitions are present
    assert 'id="arrow-small"' in rendered, "Missing arrow-small marker definition"
    assert 'id="arrow-large"' in rendered, "Missing arrow-large marker definition"
    assert 'id="circle"' in rendered, "Missing circle marker definition"
    assert 'id="star"' in rendered, "Missing star marker definition"
    
    # Verify the <defs> block exists and contains markers
    assert '<defs>' in rendered, "Missing <defs> block"
    assert '</defs>' in rendered, "Missing closing </defs> tag"
    
    # Verify defs appears before the actual SVG content (line elements)
    defs_pos = rendered.find('<defs>')
    content_pos = rendered.find('<line')
    assert defs_pos > 0 and content_pos > 0, "Missing defs or content"
    assert defs_pos < content_pos, "<defs> should appear before content elements"
    
    print("✓ All arrow marker definitions collected from nested group")


def test_multiple_nested_groups_with_arrows():
    """Test that multiple nested groups each contribute their definitions."""
    
    def draw_x_axis(**kwargs):
        g = Group()
        g.add(arrow, x1=0, y1=0, x2=100, y2=0, stroke='red', head='arrow-small')
        return g
    
    def draw_y_axis(**kwargs):
        g = Group()
        g.add(arrow, x1=0, y1=0, x2=0, y2=100, stroke='green', head='arrow-large', tail='circle')
        return g
    
    svg = Composer((200, 200))
    svg.add(draw_x_axis)
    svg.add(draw_y_axis)
    
    rendered = svg.render()
    
    # Both marker types should be present
    assert 'id="arrow-small"' in rendered
    assert 'id="arrow-large"' in rendered
    assert 'id="circle"' in rendered
    
    print("✓ Multiple nested groups successfully collected definitions")


def test_deeply_nested_groups_with_arrows():
    """Test that deeply nested groups properly bubble up definitions."""
    
    def inner_axes(**kwargs):
        g = Group()
        g.add(arrow, x1=0, y1=0, x2=50, y2=50, stroke='purple', head='star', tail='star')
        return g
    
    def middle_wrapper(**kwargs):
        g = Group()
        g.add(comment, text="Wrapper group")
        g.add(inner_axes)
        return g
    
    def outer_wrapper(**kwargs):
        g = Group()
        g.add(comment, text="Outer wrapper")
        g.add(middle_wrapper)
        return g
    
    svg = Composer((200, 200))
    svg.add(outer_wrapper)
    
    rendered = svg.render()
    
    # Star marker should be collected even from deeply nested group
    assert 'id="star"' in rendered, "Star marker missing from deeply nested group"
    
    # Both comments should be present
    assert '<!-- Wrapper group -->' in rendered
    assert '<!-- Outer wrapper -->' in rendered
    
    print("✓ Deeply nested groups properly propagate definitions")


if __name__ == '__main__':
    test_nested_group_arrow_definitions()
    test_multiple_nested_groups_with_arrows()
    test_deeply_nested_groups_with_arrows()
    print("\n✅ All tests passed!")
