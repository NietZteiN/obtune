#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::map<long,long>> f(std::vector<std::tuple<long, std::string>> items) {
    std::vector<std::map<long,long>> result;
    for (auto number : items) {
        std::map<long, long> d;
        for(auto &i : items) {
            d[std::get<0>(i)] = std::get<0>(i);
        }
        if(!d.empty()) d.erase(std::prev(d.end()));
        result.push_back(d);
        items.pop_back();
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::tuple<long, std::string>>({(std::tuple<long, std::string>)std::make_tuple(1, "pos")}))) == (std::vector<std::map<long,long>>({(std::map<long,long>)std::map<long,long>()})));
}
