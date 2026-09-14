#include<assert.h>
#include<bits/stdc++.h>

union Union_std_string_std_vector_std_string_{
    std::string f0;
    std::vector<std::string> f1;
    Union_std_string_std_vector_std_string_(std::string _f0) : f0(_f0) {}
    Union_std_string_std_vector_std_string_(std::vector<std::string> _f1) : f1(_f1) {}
    ~Union_std_string_std_vector_std_string_() {}
    bool operator==(std::string f) {
        return f0 == f ;
    }
    bool operator==(std::vector<std::string> f) {
        return f1 == f ;
    }
};

Union_std_string_std_vector_std_string_ f(std::vector<std::string> instagram, std::vector<std::string> imgur, long wins) {
    std::vector<std::vector<std::string>> photos = {instagram, imgur};
    if (instagram == imgur) {
        return Union_std_string_std_vector_std_string_(std::to_string(wins));
    }
    if (wins == 1) {
        return Union_std_string_std_vector_std_string_(photos.back());
    } else {
        std::reverse(photos.begin(), photos.end());
        return Union_std_string_std_vector_std_string_(photos.back());
    }}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"sdfs", (std::string)"drcr", (std::string)"2e"})), (std::vector<std::string>({(std::string)"sdfs", (std::string)"dr2c", (std::string)"QWERTY"})), (0)) == std::vector<std::string>({(std::string)"sdfs", (std::string)"drcr", (std::string)"2e"}));
}
