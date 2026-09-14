#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> array, long elem) {
    std::reverse(array.begin(), array.end());
    int found = -1;
    try {
        found = std::find(array.begin(), array.end(), elem) - array.begin();
    } catch (...) {
        std::reverse(array.begin(), array.end());
    }
    std::reverse(array.begin(), array.end());
    return found;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)5, (long)-3, (long)3, (long)2})), (2)) == (0));
}
