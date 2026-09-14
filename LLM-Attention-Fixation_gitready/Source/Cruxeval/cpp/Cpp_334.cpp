#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string a, std::vector<std::string> b) {
    return std::accumulate(std::next(b.begin()), b.end(), b.front(), [&](std::string result, const std::string &element) {
        return result + a + element;
    });
}
int main() {
    auto candidate = f;
    assert(candidate(("00"), (std::vector<std::string>({(std::string)"nU", (std::string)" 9 rCSAz", (std::string)"w", (std::string)" lpA5BO", (std::string)"sizL", (std::string)"i7rlVr"}))) == ("nU00 9 rCSAz00w00 lpA5BO00sizL00i7rlVr"));
}
