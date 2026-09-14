#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::vector<long> ints) {
    std::vector<long> counts(301, 0);

    for (int i : ints) {
        counts[i]++;
    }

    std::vector<std::string> r;
    for (int i = 0; i < counts.size(); i++) {
        if (counts[i] >= 3) {
            r.push_back(std::to_string(i));
        }
    }
    counts.clear();

    return std::accumulate(std::begin(r), std::end(r), std::string(), [](const std::string& a, const std::string& b) {
        return a + (a.length() > 0 ? " " : "") + b;
    });
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)2, (long)3, (long)5, (long)2, (long)4, (long)5, (long)2, (long)89}))) == ("2"));
}
