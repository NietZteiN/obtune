#include<assert.h>
#include<bits/stdc++.h>
std::map<long,long> f(std::map<long,long> dict0) {
    std::map<long,long> new_dict = dict0;
    std::vector<long> keys;
    for (auto const& pair: new_dict)
    {
        keys.push_back(pair.first);
    }
    sort(keys.begin(), keys.end());
    for (long i = 0; i < keys.size()-1; i++)
    {
        dict0[keys[i]] = i;
    }
    return dict0;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,long>({{2, 5}, {4, 1}, {3, 5}, {1, 3}, {5, 1}}))) == (std::map<long,long>({{2, 1}, {4, 3}, {3, 2}, {1, 0}, {5, 1}})));
}
