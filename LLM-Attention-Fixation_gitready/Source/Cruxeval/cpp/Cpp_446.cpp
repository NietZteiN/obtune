#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array) {
    int l = array.size();
    if (l % 2 == 0) {
        array.clear();
    } else {
        std::reverse(array.begin(), array.end());
    }
    return array;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>())) == (std::vector<long>()));
}
