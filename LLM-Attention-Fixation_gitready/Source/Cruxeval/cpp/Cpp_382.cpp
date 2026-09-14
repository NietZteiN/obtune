#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::map<long,std::string> a) {
    std::stringstream ss;
    std::map<long, std::string> s(a.rbegin(), a.rend());
    for (auto& kv : s) {
        ss << "(" << kv.first << ", '" << kv.second << "') ";
    }
    std::string result = ss.str();
    if (!result.empty()) {
        result.pop_back();
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,std::string>({{15, "Qltuf"}, {12, "Rwrepny"}}))) == ("(12, 'Rwrepny') (15, 'Qltuf')"));
}
