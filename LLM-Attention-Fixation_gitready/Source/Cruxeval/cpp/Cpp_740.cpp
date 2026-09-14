#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> plot, long delin) {
    auto it = std::find(plot.begin(), plot.end(), delin);
    if (it != plot.end()) {
        size_t split = std::distance(plot.begin(), it);
        std::vector<long> first(plot.begin(), plot.begin() + split);
        std::vector<long> second(plot.begin() + split + 1, plot.end());
        first.insert(first.end(), second.begin(), second.end());
        return first;
    } else {
        return plot;
    }
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)3, (long)4})), (3)) == (std::vector<long>({(long)1, (long)2, (long)4})));
}
