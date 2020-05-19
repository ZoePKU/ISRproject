// 模拟后台接口
function getData(params) {
	var data = [
		{id: 1},
		{id: 2},
		{id: 3},
		{id: 4},
		{id: 5},
		{id: 6},
		{id: 7},
		{id: 8},
		{id: 9},
		{id: 10},
		{id: 11},
		{id: 12},
		{id: 13},
		{id: 14},
		{id: 15},
		{id: 16}
	]

	var start = (params.current - 1) * params.size;
	var end = params.current *params.size;
	
	return {
		total: data.length,
		list: data.splice( (params.current - 1) * params.size, params.size )
	}
}

// 设置tbody的html
function setTbody (arr) {
	var html = '';
	for (var i = 0; i < arr.length; i++) {
		var item = arr[i];
		html += '<tr><td>' + item.id + '</td><td>' + item.name + '</td><td>' + item.age + '</td></tr>';
	}
	$('.tbody').html(html);
}



// 初始化分页
$('.box2').MyPaging({
	size: 3,
	total: 0,
	current: 1,
	prevHtml: '上一页',
	nextHtml: '下一页',
	layout: 'total, totalPage, prev, pager, next, jumper',
	jump: function () {
		var _this = this;

		// 模拟ajax获取数据
		setTimeout(function () {
			var res = getData({
				size: _this.size,
				current: _this.current
			})

			setTbody(res.list);

			// 必须调用
			_this.setTotal(res.total);
		}, 100);
	}
});