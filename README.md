# zhiwang
简单爬取知网的程序。2020年初的版本，不保证现在可用，只供大家参考。
具体可以看[我的博客](https://blog.csdn.net/qq_36618444/article/details/106592171)

简单介绍一下思路。知网中的每一篇论文都存在一个唯一的id，不同id对应的文章URL不同。因此第一步是获取到文章的id，然后根据id更改URL，跳转到论文的详细页面，获取更为全面的数据。

但是，知网有良好的导出系统，如果所需的字段（比如作者、论文Titile等）在支持导出的字段里，推荐使用知网自带的导出方式，爬虫并不是百试百灵。

此外，也有一些对非程序员友好的爬虫工具，比如八爪鱼（八爪鱼打钱），可以很快捷地自动选择所需字段。

# WebOfScience
爬取WebOfScience是一个比繁琐的工作，因为反扒机制做得很好需要在爬取的时候保证浏览器一直登录，时刻保证Cookie可用。
