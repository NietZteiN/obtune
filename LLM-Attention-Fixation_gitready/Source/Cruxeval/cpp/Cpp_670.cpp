#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<std::string> a, std::vector<long> b) {
    std::map<std::string, long> d;
    for(int i = 0; i < a.size(); i++)
        d[a[i]] = b[i];
    std::sort(a.begin(), a.end(), [&](std::string x, std::string y) { return d[x] > d[y]; });
    std::vector<long> result;
    for(auto& x : a) {
        result.push_back(d[x]);
        d.erase(x);
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"12", (std::string)"ab"})), (std::vector<long>({(long)2, (long)2}))) == (std::vector<long>({(long)2, (long)2})));
}
