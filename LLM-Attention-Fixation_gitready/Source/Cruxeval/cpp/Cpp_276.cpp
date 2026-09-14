#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> a) {
    if (a.size() >= 2 && a[0] > 0 && a[1] > 0) {
        std::reverse(a.begin(), a.end());
        return a;
    }
    a.push_back(0);
    return a;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>())) == (std::vector<long>({(long)0})));
}
