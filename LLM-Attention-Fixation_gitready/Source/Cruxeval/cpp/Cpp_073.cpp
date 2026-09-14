#include<assert.h>
#include<bits/stdc++.h>
std::tuple<long, long> f(std::string row) {
    return std::make_tuple(std::count(row.begin(), row.end(), '1'), std::count(row.begin(), row.end(), '0'));
}
int main() {
    auto candidate = f;
    assert(candidate(("100010010")) == (std::make_tuple(3, 6)));
}
