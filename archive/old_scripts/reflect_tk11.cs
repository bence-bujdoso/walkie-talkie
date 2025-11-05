using System;
using System.Reflection;
using System.Linq;
using System.IO;
using System.Text;

class TK11Analyzer
{
    static void Main(string[] args)
    {
        try
        {
            string exePath = "TK11.exe";
            if (!File.Exists(exePath))
            {
                Console.WriteLine("ERROR: " + exePath + " not found!");
                return;
            }

            Console.WriteLine("================================================================================");
            Console.WriteLine("TK11.exe .NET Reflection Analysis");
            Console.WriteLine("================================================================================\n");

            // Load the assembly
            Console.WriteLine("[*] Loading assembly...");
            Assembly assembly = Assembly.LoadFrom(exePath);

            Console.WriteLine("[+] Assembly loaded: " + assembly.FullName);
            Console.WriteLine("[+] Location: " + assembly.Location + "\n");

            // Get all types
            Type[] types = assembly.GetTypes();
            Console.WriteLine("[*] Found " + types.Length + " types\n");

            // Search for validation-related types and methods
            Console.WriteLine("[*] Searching for validation-related methods...\n");

            StringBuilder report = new StringBuilder();
            report.AppendLine("================================================================================");
            report.AppendLine("TK11.exe VALIDATION CODE ANALYSIS");
            report.AppendLine("================================================================================\n");

            bool found = false;

            foreach (Type type in types)
            {
                try
                {
                    // Get all methods in this type
                    MethodInfo[] methods = type.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance);

                    foreach (MethodInfo method in methods)
                    {
                        // Check if method name contains validation keywords
                        string methodName = method.Name.ToLower();
                        bool isInteresting = methodName.Contains("valid") ||
                                           methodName.Contains("check") ||
                                           methodName.Contains("firmware") ||
                                           methodName.Contains("version") ||
                                           methodName.Contains("update");

                        if (isInteresting)
                        {
                            found = true;
                            Console.WriteLine("[+] Found: " + type.FullName + "." + method.Name);

                            report.AppendLine("\nClass: " + type.FullName);
                            report.AppendLine("Method: " + method.Name);
                            report.AppendLine("Return Type: " + method.ReturnType);

                            ParameterInfo[] parameters = method.GetParameters();
                            if (parameters.Length > 0)
                            {
                                report.AppendLine("Parameters:");
                                foreach (ParameterInfo param in parameters)
                                {
                                    report.AppendLine("  - " + param.ParameterType + " " + param.Name);
                                }
                            }

                            // Try to get method body (IL)
                            try
                            {
                                MethodBody body = method.GetMethodBody();
                                if (body != null)
                                {
                                    report.AppendLine("IL Code Size: " + body.GetILAsByteArray().Length + " bytes");

                                    // Get local variables
                                    var locals = body.LocalVariables;
                                    if (locals.Count > 0)
                                    {
                                        report.AppendLine("Local Variables:");
                                        foreach (var local in locals)
                                        {
                                            report.AppendLine("  - " + local.LocalType);
                                        }
                                    }
                                }
                            }
                            catch { }

                            report.AppendLine(new string('-', 80));
                        }
                    }

                    // Check for fields that might be checksums or validation flags
                    FieldInfo[] fields = type.GetFields(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance);
                    foreach (FieldInfo field in fields)
                    {
                        string fieldName = field.Name.ToLower();
                        if (fieldName.Contains("version") || fieldName.Contains("checksum") || fieldName.Contains("valid"))
                        {
                            Console.WriteLine("[+] Found field: " + type.FullName + "." + field.Name + " (" + field.FieldType + ")");
                            report.AppendLine("\nField: " + type.FullName + "." + field.Name);
                            report.AppendLine("Type: " + field.FieldType);
                            report.AppendLine(new string('-', 80));
                        }
                    }
                }
                catch (Exception ex)
                {
                    // Skip problematic types
                }
            }

            if (!found)
            {
                Console.WriteLine("[-] No obvious validation methods found by name");
                Console.WriteLine("[*] Listing all types for manual inspection:\n");

                for (int i = 0; i < Math.Min(50, types.Length); i++)
                {
                    Console.WriteLine("  - " + types[i].FullName);
                }

                if (types.Length > 50)
                {
                    Console.WriteLine("  ... and " + (types.Length - 50) + " more");
                }
            }

            // Save report
            string reportFile = "tk11_reflection_report.txt";
            File.WriteAllText(reportFile, report.ToString(), Encoding.UTF8);
            Console.WriteLine("\n[+] Full report saved to: " + reportFile);

            // Search for string resources
            Console.WriteLine("\n[*] Searching for embedded resources...");
            string[] resourceNames = assembly.GetManifestResourceNames();
            if (resourceNames.Length > 0)
            {
                Console.WriteLine("[+] Found " + resourceNames.Length + " embedded resources:");
                foreach (string resName in resourceNames)
                {
                    Console.WriteLine("  - " + resName);
                }
            }

            Console.WriteLine("\n[*] Analysis complete!");

        }
        catch (Exception ex)
        {
            Console.WriteLine("ERROR: " + ex.Message);
            Console.WriteLine("Stack trace: " + ex.StackTrace);
        }
    }
}