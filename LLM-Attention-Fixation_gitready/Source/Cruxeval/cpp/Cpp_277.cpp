#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> lst, long mode) {
    std::vector<long> result(lst.begin(), lst.end());
    if (mode) {
        std::reverse(result.begin(), result.end());
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)3, (long)4})), (1)) == (std::vector<long>({(long)4, (long)3, (long)2, (long)1})));
}
