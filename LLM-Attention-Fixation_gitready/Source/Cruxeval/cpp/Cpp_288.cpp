#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::tuple<long, long>> f(std::map<long,long> d) {
    std::vector<std::tuple<long, long>> sorted_pairs(d.begin(), d.end());
    std::sort(sorted_pairs.begin(), sorted_pairs.end(), [](const std::tuple<long, long>& x, const std::tuple<long, long>& y) {
        return std::to_string(std::get<0>(x) + std::get<1>(x)).length() < std::to_string(std::get<0>(y) + std::get<1>(y)).length();
    });

    std::vector<std::tuple<long, long>> result;
    for (const auto& pair : sorted_pairs) {
        if (std::get<0>(pair) < std::get<1>(pair)) {
            result.push_back(pair);
        }
    }

    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,long>({{55, 4}, {4, 555}, {1, 3}, {99, 21}, {499, 4}, {71, 7}, {12, 6}}))) == (std::vector<std::tuple<long, long>>({(std::tuple<long, long>)std::make_tuple(1, 3), (std::tuple<long, long>)std::make_tuple(4, 555)})));
}
