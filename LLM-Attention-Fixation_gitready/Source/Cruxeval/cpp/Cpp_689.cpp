#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> arr) {
    int count = arr.size();
    std::vector<long> sub = arr;
    for (int i = 0; i < count; i += 2) {
        sub[i] *= 5;
    }
    return sub;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)-3, (long)-6, (long)2, (long)7}))) == (std::vector<long>({(long)-15, (long)-6, (long)10, (long)7})));
}
