#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> items) {
    std::vector<long> odd_positioned;
    while (items.size() > 0) {
        std::vector<long>::iterator result = std::min_element(items.begin(), items.end());
        int position = std::distance(items.begin(), result);
        items.erase(items.begin() + position);
        long item = items[position];
        items.erase(items.begin() + position);
        odd_positioned.push_back(item);
    }
    return odd_positioned;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)3, (long)4, (long)5, (long)6, (long)7, (long)8}))) == (std::vector<long>({(long)2, (long)4, (long)6, (long)8})));
}
