#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> values, long item1, long item2) {
    if (values.back() == item2) {
        if (std::find(values.begin() + 1, values.end(), values[0]) == values.end()) {
            values.push_back(values[0]);
        }
    } else if (values.back() == item1) {
        if (values[0] == item2) {
            values.push_back(values[0]);
        }
    }
    return values;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)1})), (2), (3)) == (std::vector<long>({(long)1, (long)1})));
}
