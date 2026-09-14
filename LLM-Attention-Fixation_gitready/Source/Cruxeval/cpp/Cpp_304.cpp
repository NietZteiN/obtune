#include<assert.h>
#include<bits/stdc++.h>
std::map<long,long> f(std::map<long,long> d) {
    std::map<long, long> result;
    auto it = std::max_element(d.begin(), d.end(), 
        [](const std::pair<long, long>& p1, const std::pair<long, long>& p2) {
            return p1.first < p2.first;
        });
    result[it->first] = it->second;
    d.erase(it);
    
    it = std::max_element(d.begin(), d.end(), 
        [](const std::pair<long, long>& p1, const std::pair<long, long>& p2) {
            return p1.first < p2.first;
        });
    result[it->first] = it->second;
    d.erase(it);
    
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,long>({{2, 3}, {17, 3}, {16, 6}, {18, 6}, {87, 7}}))) == (std::map<long,long>({{87, 7}, {18, 6}})));
}
