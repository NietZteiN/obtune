#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> album_sales) {
    while(album_sales.size() != 1) {
        album_sales.push_back(album_sales[0]);
        album_sales.erase(album_sales.begin());
    }
    return album_sales[0];
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)6}))) == (6));
}
