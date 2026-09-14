#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> lst) {
    for (int i = lst.size() - 1; i >= 1; i--) {
        for (int j = 0; j < i; j++) {
            if (lst[j] > lst[j + 1]) {
                std::swap(lst[j], lst[j + 1]);
            }
        }
    }
    return lst;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)63, (long)0, (long)1, (long)5, (long)9, (long)87, (long)0, (long)7, (long)25, (long)4}))) == (std::vector<long>({(long)0, (long)0, (long)1, (long)4, (long)5, (long)7, (long)9, (long)25, (long)63, (long)87})));
}
