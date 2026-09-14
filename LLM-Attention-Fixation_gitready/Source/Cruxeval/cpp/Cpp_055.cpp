#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array) {
    std::vector<long> array_2;
    for (long i : array) {
        if (i > 0) {
            array_2.push_back(i);
        }
    }
    std::sort(array_2.begin(), array_2.end(), std::greater<long>());
    return array_2;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)4, (long)8, (long)17, (long)89, (long)43, (long)14}))) == (std::vector<long>({(long)89, (long)43, (long)17, (long)14, (long)8, (long)4})));
}
