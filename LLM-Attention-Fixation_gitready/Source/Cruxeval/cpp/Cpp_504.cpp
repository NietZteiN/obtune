#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> values) {
    std::sort(values.begin(), values.end());
    return values;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)1, (long)1, (long)1}))) == (std::vector<long>({(long)1, (long)1, (long)1, (long)1})));
}
