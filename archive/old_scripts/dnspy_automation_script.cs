// dnSpy Automation Script
// Paste this into dnSpy's Script tab and run
using System;
using System.Linq;
using dnSpy.Contracts.Scripting;

public class FindValidation {
    public void Execute(IScriptGlobals globals) {
        var asm = globals.LoadedAssemblies.FirstOrDefault();
        if (asm == null) {
            Console.WriteLine("No assembly loaded");
            return;
        }

        Console.WriteLine("Searching for validation methods...");

        foreach (var type in asm.GetTypes()) {
            foreach (var method in type.GetMethods()) {
                var body = method.Body;
                if (body != null) {
                    var il = body.ToString();
                    if (il.Contains("File version is Wrong") ||
                        il.Contains("文件版本错误")) {
                        Console.WriteLine($"Found in: {type.FullName}.{method.Name}");
                        Console.WriteLine($"Method: {method}");
                    }
                }
            }
        }
    }
}
