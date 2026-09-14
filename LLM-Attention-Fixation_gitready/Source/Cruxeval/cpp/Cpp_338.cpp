#include<assert.h>
#include<bits/stdc++.h>
std::map<long,std::string> f(std::map<std::string,long> my_dict) {
    std::map<long, std::string> result;
    for(const auto& pair : my_dict) {
        result[pair.second] = pair.first;
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"a", 1}, {"b", 2}, {"c", 3}, {"d", 2}}))) == (std::map<long,std::string>({{1, "a"}, {2, "d"}, {3, "c"}})));
}
