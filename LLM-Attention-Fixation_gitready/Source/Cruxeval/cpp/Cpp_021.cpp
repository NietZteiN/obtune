#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array) {
    long n = array.back();
    array.pop_back();
    array.push_back(n);
    array.push_back(n);
    return array;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)1, (long)2, (long)2}))) == (std::vector<long>({(long)1, (long)1, (long)2, (long)2, (long)2})));
}
