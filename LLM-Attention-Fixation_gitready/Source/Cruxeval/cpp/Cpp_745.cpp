#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string address) {
    size_t suffix_start = address.find('@') + 1;
    if (std::count(address.begin() + suffix_start, address.end(), '.') > 1) {
        std::vector<std::string> parts;
        std::istringstream iss(address);
        std::string token;
        while (std::getline(iss, token, '@')) {
            parts.push_back(token);
        }
        address = address.substr(0, suffix_start) + parts[1].substr(0, parts[1].find('.')) + parts[1].substr(parts[1].find('.'));
    }
    return address;
}
int main() {
    auto candidate = f;
    assert(candidate(("minimc@minimc.io")) == ("minimc@minimc.io"));
}
