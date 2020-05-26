
<!--传按钮提交函数-->
   function submitpic(){
       if confirm(""){
           //确认执行时的代码
       }else{
           return;//取消执行时的代码
       }
   }

<!--图片大小自动调整-->
    function adapt(){
        var tableWidth = $("#imgTable").width(); //表格宽度
        var img = new Image();
        img.src =$('#imgs').attr("src") ;
        var imgWidth = img.width; //图片实际宽度
        if(imgWidth<tableWidth){
            $('#imgs').attr("style","width: auto");
        }else{
            $('#imgs').attr("style","width: 100%");
        }
    }
