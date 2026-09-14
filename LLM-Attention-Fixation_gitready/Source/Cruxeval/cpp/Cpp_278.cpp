#include<assert.h>
#include<bits/stdc++.h>
std::map<long,std::vector<long>> f(std::vector<long> array1, std::vector<long> array2) {
    std::map<long, std::vector<long>> result;
    for (long key : array1) {
        std::vector<long> values;
        for (long el : array2) {
            if (key * 2 > el) {
                values.push_back(el);
            }
        }
        result[key] = values;
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)0, (long)132})), (std::vector<long>({(long)5, (long)991, (long)32, (long)997}))) == (std::map<long,std::vector<long>>({{0, std::vector<long>()}, {132, std::vector<long>({(long)5, (long)32})}})));
}
