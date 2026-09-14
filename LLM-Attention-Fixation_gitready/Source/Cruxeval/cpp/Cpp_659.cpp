#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<std::string> bots) {
    std::vector<std::string> clean;
    for (const std::string& username : bots) {
        if (username.find_first_not_of("ABCDEFGHIJKLMNOPQRSTUVWXYZ") != std::string::npos) {
            clean.push_back(username.substr(0, 2) + username.substr(username.length() - 3));
        }
    }
    return clean.size();
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"yR?TAJhIW?n", (std::string)"o11BgEFDfoe", (std::string)"KnHdn2vdEd", (std::string)"wvwruuqfhXbGis"}))) == (4));
}
