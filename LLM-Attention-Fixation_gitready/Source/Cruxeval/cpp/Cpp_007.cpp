#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> list) {
    std::vector<long> original = list;
    while (list.size() > 1) {
        list.pop_back();
        for (size_t i = 0; i < list.size(); i++) {
            list.erase(list.begin() + i);
        }
    }
    list = original;
    if (!list.empty()) {
        list.erase(list.begin());
    }
    return list;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>())) == (std::vector<long>()));
}
