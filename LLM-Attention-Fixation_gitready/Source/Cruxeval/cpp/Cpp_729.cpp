#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::string s1, std::string s2) {
    std::vector<long> res;
    size_t i = s1.rfind(s2);
    while (i != std::string::npos) {
        res.push_back(i + s2.size() - 1);
        if (i == 0) break;
        i = s1.rfind(s2, i - 1);
    }
    return res;
}
int main() {
    auto candidate = f;
    assert(candidate(("abcdefghabc"), ("abc")) == (std::vector<long>({(long)10, (long)2})));
}
