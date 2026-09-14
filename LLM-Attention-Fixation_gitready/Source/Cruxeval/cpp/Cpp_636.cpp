#include<assert.h>
#include<bits/stdc++.h>
std::map<long,std::string> f(std::map<long,std::string> d) {
    std::map<long,std::string> r;
    while (!d.empty()) {
        for (auto const& pair : d) {
            r[pair.first] = pair.second;
        }
        auto it = d.end();
        --it;
        d.erase(it);
    }
    return r;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,std::string>({{3, "A3"}, {1, "A1"}, {2, "A2"}}))) == (std::map<long,std::string>({{3, "A3"}, {1, "A1"}, {2, "A2"}})));
}
