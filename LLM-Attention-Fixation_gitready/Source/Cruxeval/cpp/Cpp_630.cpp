#include<assert.h>
#include<bits/stdc++.h>
std::map<long,long> f(std::map<long,long> original, std::map<long,long> string) {
    std::map<long, long> temp(original.begin(), original.end());
    for (auto& elem : string) {
        temp[elem.second] = elem.first;
    }
    return temp;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,long>({{1, -9}, {0, -7}})), (std::map<long,long>({{1, 2}, {0, 3}}))) == (std::map<long,long>({{1, -9}, {0, -7}, {2, 1}, {3, 0}})));
}
