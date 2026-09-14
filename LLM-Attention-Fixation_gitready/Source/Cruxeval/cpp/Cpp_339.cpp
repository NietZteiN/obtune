#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> array, long elem) {
    int d = 0;
    std::string elem_str = std::to_string(elem);
    for (int i : array) {
        if (std::to_string(i) == elem_str) {
            d++;
        }
    }
    return d;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)-1, (long)2, (long)1, (long)-8, (long)-8, (long)2})), (2)) == (2));
}
