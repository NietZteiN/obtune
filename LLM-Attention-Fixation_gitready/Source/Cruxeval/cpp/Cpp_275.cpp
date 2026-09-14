#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::map<long,std::string> dic) {
    std::map<std::string, long> dic2;
    for(auto const& pair : dic) {
        dic2[pair.second] = pair.first;
    }
    return dic2;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,std::string>({{-1, "a"}, {0, "b"}, {1, "c"}}))) == (std::map<std::string,long>({{"a", -1}, {"b", 0}, {"c", 1}})));
}
