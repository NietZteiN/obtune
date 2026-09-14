#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> array, long elem) {
    int ind = std::find(array.begin(), array.end(), elem) - array.begin();
    return ind * 2 + array[array.size() - ind - 1] * 3;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)-1, (long)2, (long)1, (long)-8, (long)2})), (2)) == (-22));
}
