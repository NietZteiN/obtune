#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::tuple<std::string, long>> f(std::map<std::string,long> dic) {
    while (dic.size() > 1) {
        auto it = std::min_element(dic.begin(), dic.end(),
            [](const std::pair<std::string, long>& a,
               const std::pair<std::string, long>& b) {
                return a.first.size() < b.first.size();
            });
        dic.erase(it);
    }
    std::vector<std::tuple<std::string, long>> result;
    for (const auto& p : dic) {
        result.push_back(std::make_tuple(p.first, p.second));
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"11", 52}, {"65", 34}, {"a", 12}, {"4", 52}, {"74", 31}}))) == (std::vector<std::tuple<std::string, long>>({(std::tuple<std::string, long>)std::make_tuple("74", 31)})));
}
