#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::string s) {
    std::map<std::string, long> count;
    for (char i : s) {
        if (std::islower(i)) {
            count[std::string(1, std::tolower(i))] = std::count(s.begin(), s.end(), std::tolower(i)) + count[std::string(1, std::tolower(i))];
        } else {
            count[std::string(1, std::tolower(i))] = std::count(s.begin(), s.end(), std::toupper(i)) + count[std::string(1, std::tolower(i))];
        }
    }
    return count;
}
int main() {
    auto candidate = f;
    assert(candidate(("FSA")) == (std::map<std::string,long>({{"f", 1}, {"s", 1}, {"a", 1}})));
}
