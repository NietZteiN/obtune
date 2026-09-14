#include<assert.h>
#include<bits/stdc++.h>
union Union_long_std_string{
    long f0;
    std::string f1;    Union_long_std_string(long _f0) : f0(_f0) {}
    Union_long_std_string(std::string _f1) : f1(_f1) {}
    ~Union_long_std_string() {}
    bool operator==(long f) {
        return f0 == f ;
    }    bool operator==(std::string f) {
        return f1 == f ;
    }
};
Union_long_std_string f(std::string items, std::string target) {
    std::stringstream ss(items);
    std::string item;
    while (ss >> item) {
        if (target.find(item) != std::string::npos) {
            return Union_long_std_string(items.find(item) + 1);
        }
        if (item.find('.') == item.length() - 1 || item.find('.') == 0) {
            return Union_long_std_string("error");
        }
    }
    return Union_long_std_string(".");
}
int main() {
    auto candidate = f;
    assert(candidate(("qy. dg. rnvprt rse.. irtwv tx.."), ("wtwdoacb")) == "error");
}
