#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> array, long elem) {
    return std::count(array.begin(), array.end(), elem) + elem;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)1, (long)1})), (-2)) == (-2));
}
