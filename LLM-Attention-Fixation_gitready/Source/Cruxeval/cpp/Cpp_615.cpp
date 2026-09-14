#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> in_list, long num) {
    in_list.push_back(num);
    return std::distance(in_list.begin(), std::max_element(in_list.begin(), in_list.end() - 1));
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)-1, (long)12, (long)-6, (long)-2})), (-1)) == (1));
}
