#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<std::string> names) {
    int count = names.size();
    int numberOfNames = 0;
    for (std::string name : names) {
        bool isAlpha = true;
        for (char c : name) {
            if (!isalpha(c)) {
                isAlpha = false;
                break;
            }
        }
        if (isAlpha) {
            numberOfNames++;
        }
    }
    return numberOfNames;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"sharron", (std::string)"Savannah", (std::string)"Mike Cherokee"}))) == (2));
}
