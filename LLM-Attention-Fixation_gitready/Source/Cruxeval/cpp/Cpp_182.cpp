#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::tuple<std::string, long>> f(std::map<std::string,long> dic) {
    std::vector<std::tuple<std::string, long>> result;
    std::vector<std::pair<std::string, long>> temp(dic.begin(), dic.end());
    std::sort(temp.begin(), temp.end(), [](const auto& x, const auto& y) {
        return x.first < y.first;
    });
    
    for (const auto& pair : temp) {
        result.push_back(std::make_tuple(pair.first, pair.second));
    }
    
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"b", 1}, {"a", 2}}))) == (std::vector<std::tuple<std::string, long>>({(std::tuple<std::string, long>)std::make_tuple("a", 2), (std::tuple<std::string, long>)std::make_tuple("b", 1)})));
}
