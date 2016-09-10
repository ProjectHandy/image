namespace cpp image
namespace cocoa image

service Images {
  list<binary> getSellItemImages(1:string id),
  void postSellItemImages(1:string id, 2:list<binary> images),
  binary getBookCoverImage(1:string isbn),
  list<string> queryIsbn(1:string isbn),
}
